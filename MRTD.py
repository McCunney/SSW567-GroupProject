# MRTD.py

def scan_mrz_from_device():
    """
    Simulates receiving two MRZ strings from a scanner hardware.
    NOTE: Stub for integration with actual hardware.
    """
    pass  # To be mocked during testing


def decode_mrz(line1, line2):
    """
    Decodes two MRZ strings into a dictionary of fields and extracts check digits.
    Returns parsed fields and check digits.
    """
    try:
        result = {
            "document_type": line1[0:2],
            "issuing_country": line1[2:5],
            "name": line1[5:44].replace("<", " ").strip(),
            "passport_number": line2[0:9],
            "passport_number_check_digit": line2[9],
            "nationality": line2[10:13],
            "birth_date": line2[13:19],
            "birth_date_check_digit": line2[19],
            "sex": line2[20],
            "expiry_date": line2[21:27],
            "expiry_date_check_digit": line2[27],
        }
        return result
    except IndexError:
        return {"error": "Invalid MRZ format"}


def encode_mrz_fields(data):
    """
    Encodes a dictionary of travel document fields into MRZ lines (as strings).
    Assumes all required fields are provided.
    """
    try:
        line1 = (
            data["document_type"].ljust(2, "<") +
            data["issuing_country"].ljust(3, "<") +
            data["name"].replace(" ", "<").ljust(39, "<")
        )

        line2 = (
            data["passport_number"].ljust(9, "<") +
            data["passport_number_check_digit"] +
            data["nationality"].ljust(3, "<") +
            data["birth_date"] +
            data["birth_date_check_digit"] +
            data["sex"] +
            data["expiry_date"] +
            data["expiry_date_check_digit"]
        )

        return line1, line2
    except KeyError as e:
        return {"error": f"Missing field: {e}"}


def validate_check_digits(decoded_fields):
    """
    Compares each field's computed check digit with its actual check digit.
    Returns a list of mismatches.
    """

    def compute_check_digit(data):
        weights = [7, 3, 1]
        total = 0
        for i, char in enumerate(data):
            if char.isdigit():
                val = int(char)
            elif char.isalpha():
                val = ord(char.upper()) - 55
            elif char == '<':
                val = 0
            else:
                return -1  # Invalid character
            total += val * weights[i % 3]
        return str(total % 10)

    mismatches = []

    passport_expected = compute_check_digit(decoded_fields["passport_number"])
    if passport_expected != decoded_fields["passport_number_check_digit"]:
        mismatches.append({
            "field": "passport_number",
            "expected": passport_expected,
            "actual": decoded_fields["passport_number_check_digit"]
        })

    birth_expected = compute_check_digit(decoded_fields["birth_date"])
    if birth_expected != decoded_fields["birth_date_check_digit"]:
        mismatches.append({
            "field": "birth_date",
            "expected": birth_expected,
            "actual": decoded_fields["birth_date_check_digit"]
        })

    expiry_expected = compute_check_digit(decoded_fields["expiry_date"])
    if expiry_expected != decoded_fields["expiry_date_check_digit"]:
        mismatches.append({
            "field": "expiry_date",
            "expected": expiry_expected,
            "actual": decoded_fields["expiry_date_check_digit"]
        })

    return mismatches

