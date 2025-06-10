use _pycrockford_rs_bindings::{
    decode_crockford_to_bytes, encode_bytes_to_crockford, CrockfordError,
};

#[test]
fn round_trip() {
    let bytes = [1u8; 16];
    let encoded = encode_bytes_to_crockford(&bytes);
    let decoded = decode_crockford_to_bytes(&encoded).unwrap();
    assert_eq!(bytes, decoded);
}

#[test]
fn decode_invalid_length() {
    let err = decode_crockford_to_bytes("ABC").unwrap_err();
    matches!(err, CrockfordError::InvalidLength(_));
}

#[test]
fn decode_invalid_character() {
    let err = decode_crockford_to_bytes("********").unwrap_err();
    matches!(err, CrockfordError::DecodeError(_));
}

#[test]
fn decode_is_case_insensitive() {
    let bytes = [0u8; 16];
    let encoded = encode_bytes_to_crockford(&bytes);
    let decoded = decode_crockford_to_bytes(&encoded.to_lowercase()).unwrap();
    assert_eq!(decoded, bytes);
}
