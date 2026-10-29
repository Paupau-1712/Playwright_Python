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

Uses GET only. Original data comes from `GET /productsList` (the response is shown in the test log); `utils/masking.py` masks it with per-field regex rules (letters -> other letters, digits -> other digits, spaces/punctuation kept; `price` masks digits only). The product `id` is retained. A side-by-side comparison (text tables in the log, plus `reports/masking_comparison.html`) shows original vs masked.

| Scenario | Expected |
| --- | --- |
| GET products response | 200, shown in the log |
| Input vs masked output | side-by-side tables |
| id | retained |
| name, brand, category, price | every value differs from the input |
| Format | same shape as the input (letters/digits/punctuation, `Rs.` prefix) |
| Original values | do not appear in the masked output |
| Same input twice | identical masked output |
| Input record | not modified |

Note: this site always answers with HTTP 200; the real status is the `responseCode` field in the JSON body, which is what the tests assert.

## UI tests (`tests/ui/`)

| Scenario | File |
| --- | --- |
| Home page title | `test_home.py` |
| Products page lists products | `test_home.py` |
| Login page is reachable | `test_home.py` |
