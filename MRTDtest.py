# MRTDtest.py

import unittest
from unittest.mock import patch
from MRTD import scan_mrz_from_device, decode_mrz, encode_mrz_fields, validate_check_digits

class TestMRTD(unittest.TestCase):

    @patch('MRTD.scan_mrz_from_device')
    def test_scan_mrz_stub(self, mock_scan):
        """Mocking MRZ scan hardware to return fixed MRZ strings."""
        mock_scan.return_value = (
            "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<",
            "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<06"
        )
        self.assertEqual(len(mock_scan()), 2)

    def test_decode_mrz_valid(self):
        """Tests decoding of valid MRZ lines."""
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159<<<<<<<<<<<<<<06"
        decoded = decode_mrz(line1, line2)
        self.assertEqual(decoded['document_type'], "P<")
        self.assertEqual(decoded['nationality'], "UTO")
        self.assertEqual(decoded['sex'], "F")

    def test_decode_mrz_invalid_format(self):
        """Test decoding with incomplete line2 string."""
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "INVALID"
        decoded = decode_mrz(line1, line2)
        self.assertIn('error', decoded)

    def test_encode_mrz_fields_success(self):
        """Tests encoding a dictionary of fields into MRZ strings."""
        fields = {
            "document_type": "P",
            "issuing_country": "UTO",
            "name": "ERIKSSON ANNA MARIA",
            "passport_number": "L898902C3",
            "passport_number_check_digit": "6",
            "nationality": "UTO",
            "birth_date": "740812",
            "birth_date_check_digit": "2",
            "sex": "F",
            "expiry_date": "120415",
            "expiry_date_check_digit": "9"
        }
        line1, line2 = encode_mrz_fields(fields)
        self.assertTrue(line1.startswith("P<UTO"))
        self.assertIn("L898902C3", line2)

    def test_encode_mrz_missing_field(self):
        """Tests handling of missing field in encoding."""
        fields = {
            "document_type": "P",
            "issuing_country": "UTO"
        }
        result = encode_mrz_fields(fields)
        self.assertIn("error", result)

    def test_validate_check_digits_all_correct(self):
        """Validates check digits and expects no mismatches."""
        decoded_fields = {
            "passport_number": "L898902C3",
            "passport_number_check_digit": "6",
            "birth_date": "740812",
            "birth_date_check_digit": "2",
            "expiry_date": "120415",
            "expiry_date_check_digit": "9"
        }
        mismatches = validate_check_digits(decoded_fields)
        self.assertEqual(len(mismatches), 0)

    def test_validate_check_digits_with_mismatch(self):
        """Simulate mismatched check digit and validate report."""
        decoded_fields = {
            "passport_number": "L898902C3",
            "passport_number_check_digit": "0",  # wrong
            "birth_date": "740812",
            "birth_date_check_digit": "2",
            "expiry_date": "120415",
            "expiry_date_check_digit": "9"
        }
        mismatches = validate_check_digits(decoded_fields)
        self.assertEqual(len(mismatches), 1)
        self.assertEqual(mismatches[0]['field'], "passport_number")

if __name__ == '__main__':
    unittest.main()

