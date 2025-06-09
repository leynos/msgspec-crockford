#![allow(non_local_definitions)]

use data_encoding::{Encoding, Specification};
use once_cell::sync::Lazy;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBytes, PyString, PyType};
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

static CROCKFORD: Lazy<Encoding> = Lazy::new(|| {
    let mut spec = Specification::new();
    spec.symbols.push_str("0123456789ABCDEFGHJKMNPQRSTVWXYZ");
    spec.translate.from = "iolIOL".into();
    spec.translate.to = "101101".into();
    spec.ignore.push('-');
    spec.encoding().unwrap()
});

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
fn encode_crockford_py(b: &[u8]) -> PyResult<String> {
    if b.len() != 16 {
        return Err(PyValueError::new_err("input must be exactly 16 bytes"));
    }
    let arr: &[u8; 16] = b.try_into().unwrap();
    Ok(encode_bytes_to_crockford(arr))
}

#[pyfunction]
fn decode_crockford_py(py: Python<'_>, s: &str) -> PyResult<Py<PyBytes>> {
    let bytes = decode_crockford_to_bytes(s).map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok(PyBytes::new(py, &bytes).into())
}

#[pyclass]
struct CrockfordUUID {
    bytes: [u8; 16],
}

#[pymethods]
#[allow(non_local_definitions)]
impl CrockfordUUID {
    #[new]
    fn new(value: &PyAny) -> PyResult<Self> {
        if let Ok(s) = value.downcast::<PyString>() {
            let bytes = decode_crockford_to_bytes(s.to_str()?)
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            Ok(Self { bytes })
        } else if let Ok(b) = value.downcast::<PyBytes>() {
            let slice = b.as_bytes();
            if slice.len() != 16 {
                return Err(PyValueError::new_err("bytes input must be 16 bytes"));
            }
            let mut arr = [0u8; 16];
            arr.copy_from_slice(slice);
            Ok(Self { bytes: arr })
        } else if let Ok(uuid_mod) = value.py().import("uuid") {
            if value.is_instance(uuid_mod.getattr("UUID")?)? {
                let py_bytes: &PyBytes = value.getattr("bytes")?.extract()?;
                let slice = py_bytes.as_bytes();
                let mut arr = [0u8; 16];
                arr.copy_from_slice(slice);
                Ok(Self { bytes: arr })
            } else {
                Err(PyValueError::new_err(
                    "expected Crockford string, 16 bytes, or uuid.UUID",
                ))
            }
        } else {
            Err(PyValueError::new_err(
                "expected Crockford string, 16 bytes, or uuid.UUID",
            ))
        }
    }

    #[getter]
    fn bytes<'py>(&self, py: Python<'py>) -> &'py PyBytes {
        PyBytes::new(py, &self.bytes)
    }

    #[getter]
    fn uuid(&self, py: Python) -> PyResult<PyObject> {
        let uuid_mod = py.import("uuid")?;
        let uuid_cls = uuid_mod.getattr("UUID")?;
        let py_bytes = PyBytes::new(py, &self.bytes);
        uuid_cls.call1((py_bytes,)).map(Into::into)
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

    #[classmethod]
    fn generate_v4(_cls: &PyType) -> Self {
        let uuid = Uuid::new_v4();
        Self {
            bytes: *uuid.as_bytes(),
        }
    }

    #[classmethod]
    fn generate_v7(_cls: &PyType) -> Self {
        let uuid = Uuid::now_v7();
        Self {
            bytes: *uuid.as_bytes(),
        }
    }
}

#[pymodule]
fn _pycrockford_rs_bindings(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(decode_crockford_py, m)?)?;
    m.add_function(wrap_pyfunction!(encode_crockford_py, m)?)?;
    m.add_class::<CrockfordUUID>()?;
    Ok(())
}
