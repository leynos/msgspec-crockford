//! Rust bindings exposing Crockford Base32 UUID helpers to Python.

use data_encoding::{Encoding, Specification};
use pyo3::basic::CompareOp;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyAny, PyBytes, PyDict, PyModule, PyString, PyType};
use pyo3::IntoPyObjectExt;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::LazyLock;
use uuid::Uuid;

#[derive(Debug)]
pub enum CrockfordError {
    InvalidLength(usize),
    DecodeError(data_encoding::DecodeError),
}

impl std::fmt::Display for CrockfordError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CrockfordError::InvalidLength(len) => write!(f, "expected 16 bytes, got {len}"),
            CrockfordError::DecodeError(e) => write!(f, "{e}"),
        }
    }
}

impl std::error::Error for CrockfordError {}

static CROCKFORD: LazyLock<Encoding> = LazyLock::new(|| {
    let mut spec = Specification::new();
    spec.symbols.push_str("0123456789ABCDEFGHJKMNPQRSTVWXYZ");
    // Accept lowercase input for all allowed characters.
    spec.translate.from = "abcdefghjkmnpqrstvwxyz".into();
    spec.translate.to = "ABCDEFGHJKMNPQRSTVWXYZ".into();
    // Handle visually similar characters per Crockford spec.
    spec.translate.from.push_str("ilILoO");
    spec.translate.to.push_str("111100");
    spec.ignore.push('-');
    spec.encoding().unwrap()
});

// Cache the 'uuid' module to avoid repeated imports at runtime.
fn uuid_module(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
    static UUID_MODULE: PyOnceLock<Py<PyModule>> = PyOnceLock::new();
    let module =
        UUID_MODULE.get_or_try_init(py, || PyModule::import(py, "uuid").map(Bound::unbind))?;
    Ok(module.bind(py).clone())
}

pub fn encode_bytes_to_crockford(bytes: &[u8; 16]) -> String {
    CROCKFORD.encode(bytes)
}

pub fn decode_crockford_to_bytes(s: &str) -> Result<[u8; 16], CrockfordError> {
    let decoded = CROCKFORD
        .decode(s.as_bytes())
        .map_err(CrockfordError::DecodeError)?;
    if decoded.len() != 16 {
        return Err(CrockfordError::InvalidLength(decoded.len()));
    }
    let mut out = [0u8; 16];
    out.copy_from_slice(&decoded);
    Ok(out)
}

#[pyfunction]
fn encode_crockford(b: &[u8]) -> PyResult<String> {
    let arr: &[u8; 16] = b
        .try_into()
        .map_err(|_| PyValueError::new_err(format!("expected 16 bytes, got {}", b.len())))?;
    Ok(encode_bytes_to_crockford(arr))
}

#[pyfunction]
fn decode_crockford(py: Python<'_>, s: &str) -> PyResult<Py<PyBytes>> {
    let bytes = decode_crockford_to_bytes(s).map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok(PyBytes::new(py, &bytes).unbind())
}

#[pyclass]
struct CrockfordUUID {
    bytes: [u8; 16],
}

impl CrockfordUUID {
    /// Build from a Crockford Base32 string.
    fn from_py_string(s: &Bound<'_, PyString>) -> PyResult<Self> {
        let bytes = decode_crockford_to_bytes(s.to_str()?)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Self { bytes })
    }

    /// Build from a raw 16-byte value.
    fn from_py_bytes(b: &Bound<'_, PyBytes>) -> PyResult<Self> {
        let slice = b.as_bytes();
        let arr: [u8; 16] = slice.try_into().map_err(|_| {
            PyValueError::new_err(format!("expected 16 bytes, got {}", slice.len()))
        })?;
        Ok(Self { bytes: arr })
    }

    /// Build from a `uuid.UUID` instance; rejects any other type.
    fn from_py_uuid(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        let uuid_mod = uuid_module(value.py())?;
        if !value.is_instance(&uuid_mod.getattr("UUID")?)? {
            return Err(PyValueError::new_err(
                "expected Crockford string, 16 bytes, or uuid.UUID",
            ));
        }
        let bytes_vec: Vec<u8> = value.getattr("bytes")?.extract()?;
        let arr: [u8; 16] = bytes_vec.as_slice().try_into().map_err(|_| {
            PyValueError::new_err(format!("expected 16 bytes, got {}", bytes_vec.len()))
        })?;
        Ok(Self { bytes: arr })
    }
}

#[pymethods]
impl CrockfordUUID {
    #[new]
    fn new(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(s) = value.cast::<PyString>() {
            Self::from_py_string(s)
        } else if let Ok(b) = value.cast::<PyBytes>() {
            Self::from_py_bytes(b)
        } else {
            Self::from_py_uuid(value)
        }
    }

    #[getter]
    fn bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.bytes)
    }

    #[getter]
    fn uuid(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let uuid_mod = uuid_module(py)?;
        let uuid_cls = uuid_mod.getattr("UUID")?;
        let kwargs = PyDict::new(py);
        kwargs.set_item("bytes", PyBytes::new(py, &self.bytes))?;
        Ok(uuid_cls.call((), Some(&kwargs))?.unbind())
    }

    fn __bytes__(&self, py: Python<'_>) -> Py<PyBytes> {
        PyBytes::new(py, &self.bytes).unbind()
    }

    fn __str__(&self) -> String {
        encode_bytes_to_crockford(&self.bytes)
    }

    fn __repr__(&self) -> String {
        format!(
            "CrockfordUUID('{}')",
            encode_bytes_to_crockford(&self.bytes)
        )
    }

    fn __hash__(&self) -> isize {
        let mut hasher = DefaultHasher::new();
        self.bytes.hash(&mut hasher);
        let mut value = hasher.finish() as isize;
        if value == -1 {
            value = -2;
        }
        value
    }

    fn __richcmp__(
        &self,
        other: PyRef<'_, Self>,
        op: CompareOp,
        py: Python<'_>,
    ) -> PyResult<Py<PyAny>> {
        match op {
            CompareOp::Eq => (self.bytes == other.bytes).into_py_any(py),
            CompareOp::Ne => (self.bytes != other.bytes).into_py_any(py),
            _ => Ok(py.NotImplemented()),
        }
    }

    #[classmethod]
    fn generate_v4(_cls: &Bound<'_, PyType>) -> Self {
        let uuid = Uuid::new_v4();
        Self {
            bytes: *uuid.as_bytes(),
        }
    }

    #[classmethod]
    fn generate_v7(_cls: &Bound<'_, PyType>) -> Self {
        let uuid = Uuid::now_v7();
        Self {
            bytes: *uuid.as_bytes(),
        }
    }
}

#[pymodule]
fn _pycrockford_rs_bindings(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(decode_crockford, m)?)?;
    m.add_function(wrap_pyfunction!(encode_crockford, m)?)?;
    m.add_class::<CrockfordUUID>()?;
    Ok(())
}
