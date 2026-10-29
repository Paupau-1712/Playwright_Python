# Test list

Source of the API scenarios: https://automationexercise.com/api_list

## API tests (`tests/api/`)

| API | Scenario | Method / Endpoint | Expected | File |
| --- | --- | --- | --- | --- |
| 1 | Get all products | GET `/productsList` | 200, product list | `test_products_list.py` |
| 2 | POST to products list | POST `/productsList` | 405 | `test_products_list.py` |
| 3 | Get all brands | GET `/brandsList` | 200, brand list | `test_brands_list.py` |
| 4 | PUT to brands list | PUT `/brandsList` | 405 | `test_brands_list.py` |
| 5 | Search product | POST `/searchProduct` | 200, matching products | `test_search_product.py` |
| 6 | Search without parameter | POST `/searchProduct` | 400 | `test_search_product.py` |
| 7 | Verify login, valid | POST `/verifyLogin` | 200, User exists! | `test_verify_login.py` |
| 8 | Verify login, no email | POST `/verifyLogin` | 400 | `test_verify_login.py` |
| 9 | DELETE verify login | DELETE `/verifyLogin` | 405 | `test_verify_login.py` |
| 10 | Verify login, invalid | POST `/verifyLogin` | 404, User not found! | `test_verify_login.py` |
| 11 | Create account | POST `/createAccount` | 201, User created! | `test_user_account.py` |
| 12 | Delete account | DELETE `/deleteAccount` | 200, Account deleted! | `test_user_account.py` |
| 13 | Update account | PUT `/updateAccount` | 200, User updated! | `test_user_account.py` |
| 14 | Get user by email (+ negative) | GET `/getUserDetailByEmail` | 200 / 404 | `test_user_account.py` |

### Data masking (`test_data_masking.py`)

Original customer data (fetched live from `getUserDetailByEmail`) goes in; `utils/masking.py` returns a synthetic, deterministic copy.

| Scenario | Expected |
| --- | --- |
| Customer id | retained unchanged |
| Personal fields (name, email, address, birth date, ...) | replaced with synthetic values |
| Original values | do not appear anywhere in the masked output |
| Masked values | well-formed (email, zipcode, name consistency) |
| Same customer twice | identical masked output |
| Different customers | different masked output |
| Input record | not modified |
| Non-personal fields (title, country) | preserved |

Note: this site always answers with HTTP 200; the real status is the `responseCode` field in the JSON body, which is what the tests assert.

## UI tests (`tests/ui/`)

| Scenario | File |
| --- | --- |
| Home page title | `test_home.py` |
| Products page lists products | `test_home.py` |
| Login page is reachable | `test_home.py` |
