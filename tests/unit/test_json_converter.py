import unittest
import json
from datetime import datetime
from pydantic import ValidationError
from src. importto_json, from_json  # Assuming your code is in 'your_module.py'

@pydantic_dataclass
class Address:
    street: str
    city: str
    zip_code: str

@pydantic_dataclass
class Product:
    product_id: int
    name: str
    description: Optional[str]
    price: float
    is_available: bool = True
    created_at: datetime
    last_modified: datetime
    supplier_address: Address

class TestJSONConversion(unittest.TestCase):

    def setUp(self):
        self.now = datetime(2025, 4, 12, 15, 10, 0)
        self.address_obj = Address(street="123 Main St", city="Tbilisi", zip_code="0101")
        self.product_obj = Product(
            product_id=1,
            name="Laptop",
            description="High-performance laptop",
            price=1200.50,
            is_available=True,
            created_at=self.now,
            last_modified=self.now,
            supplier_address=self.address_obj
        )

    def test_to_json_address(self):
        expected_json = '{"street": "123 Main St", "city": "Tbilisi", "zip_code": "0101"}'
        self.assertEqual(to_json(self.address_obj), expected_json)

    def test_to_json_product(self):
        expected_json = json.dumps({
            "product_id": 1,
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 1200.50,
            "is_available": True,
            "created_at": self.now.isoformat(),
            "last_modified": self.now.isoformat(),
            "supplier_address": {"street": "123 Main St", "city": "Tbilisi", "zip_code": "0101"}
        })
        self.assertEqual(to_json(self.product_obj), expected_json)

    def test_from_json_address(self):
        json_string = '{"street": "456 Oak Ave", "city": "Batumi", "zip_code": "0202"}'
        parsed_address = from_json(json_string, "Address")
        self.assertEqual(parsed_address.street, "456 Oak Ave")
        self.assertEqual(parsed_address.city, "Batumi")
        self.assertEqual(parsed_address.zip_code, "0202")
        self.assertIsInstance(parsed_address, Address)

    def test_from_json_product(self):
        json_string = json.dumps({
            "product_id": 2,
            "name": "Mouse",
            "description": "Wireless mouse",
            "price": 25.99,
            "is_available": True,
            "created_at": self.now.isoformat(),
            "last_modified": self.now.isoformat(),
            "supplier_address": {"street": "789 Pine Ln", "city": "Kutaisi", "zip_code": "0303"}
        })
        parsed_product = from_json(json_string, "Product")
        self.assertEqual(parsed_product.product_id, 2)
        self.assertEqual(parsed_product.name, "Mouse")
        self.assertEqual(parsed_product.price, 25.99)
        self.assertTrue(parsed_product.is_available)
        self.assertEqual(parsed_product.created_at, self.now)
        self.assertEqual(parsed_product.last_modified, self.now)
        self.assertIsInstance(parsed_product.supplier_address, Address)
        self.assertEqual(parsed_product.supplier_address.street, "789 Pine Ln")
        self.assertEqual(parsed_product.supplier_address.city, "Kutaisi")
        self.assertEqual(parsed_product.supplier_address.zip_code, "0303")
        self.assertIsInstance(parsed_product, Product)

    def test_from_json_invalid_address_data(self):
        json_string = '{"street": 123, "city": "Tbilisi", "zip_code": "0101"}'
        with self.assertRaisesRegex(ValueError, "Failed to create Address from JSON: 1 validation error for Address"):
            from_json(json_string, "Address")

    def test_from_json_invalid_product_data(self):
        json_string = json.dumps({
            "product_id": "abc",
            "name": "Laptop",
            "price": "invalid",
            "created_at": "not a datetime",
            "last_modified": "not a datetime",
            "supplier_address": {"street": 123, "city": "Tbilisi", "zip_code": "0101"}
        })
        with self.assertRaisesRegex(ValueError, "Failed to create Product from JSON: 5 validation errors for Product"):
            from_json(json_string, "Product")

    def test_from_json_invalid_json_string(self):
        json_string = '{"name": "Test", "value": }'
        with self.assertRaisesRegex(ValueError, "Invalid JSON string:"):
            from_json(json_string, "Address")

    def test_from_json_unsupported_dataclass_name(self):
        json_string = '{"key": "value"}'
        with self.assertRaisesRegex(ValueError, "Unsupported dataclass name: UnknownClass"):
            from_json(json_string, "UnknownClass")

    def test_to_json_with_none_description(self):
        product_with_none_desc = Product(
            product_id=3,
            name="Tablet",
            description=None,
            price=300.00,
            is_available=True,
            created_at=self.now,
            last_modified=self.now,
            supplier_address=self.address_obj
        )
        expected_json = json.dumps({
            "product_id": 3,
            "name": "Tablet",
            "description": None,
            "price": 300.00,
            "is_available": True,
            "created_at": self.now.isoformat(),
            "last_modified": self.now.isoformat(),
            "supplier_address": {"street": "123 Main St", "city": "Tbilisi", "zip_code": "0101"}
        })
        self.assertEqual(to_json(product_with_none_desc), expected_json)

if __name__ == '__main__':
    unittest.main()