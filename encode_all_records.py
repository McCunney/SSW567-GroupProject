import json
from MRTD import encode_mrz_fields

def compute_check_digit(data):
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data):
        if char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char.upper()) - 55  # A=10, B=11, ..., Z=35
        elif char == '<':
            val = 0
        else:
            val = 0  # For unexpected characters
        total += val * weights[i % 3]
    return str(total % 10)

with open('records_decoded.json', 'r') as f:
    decoded_data = json.load(f)

decoded_records = decoded_data["records_decoded"]

with open('records_encoded.json', 'w') as f_out:
    for record in decoded_records:
        issuing_country = record["line1"]["issuing_country"]
        last_name = record["line1"]["last_name"]
        given_name = record["line1"]["given_name"]
        passport_number = record["line2"]["passport_number"]
        nationality = record["line2"]["country_code"]
        birth_date = record["line2"]["birth_date"]
        sex = record["line2"]["sex"]
        expiry_date = record["line2"]["expiration_date"]
        personal_number = record["line2"]["personal_number"]

        passport_number_cd = compute_check_digit(passport_number)
        birth_date_cd = compute_check_digit(birth_date)
        expiry_date_cd = compute_check_digit(expiry_date)

        mrz_data = {
            "document_type": "P<",
            "issuing_country": issuing_country,
            "name": f"{last_name}<<{given_name}",
            "passport_number": passport_number,
            "passport_number_check_digit": passport_number_cd,
            "nationality": nationality,
            "birth_date": birth_date,
            "birth_date_check_digit": birth_date_cd,
            "sex": sex,
            "expiry_date": expiry_date,
            "expiry_date_check_digit": expiry_date_cd,
        }

        line1, line2 = encode_mrz_fields(mrz_data)

        f_out.write(f"{line1};{line2}\n")

