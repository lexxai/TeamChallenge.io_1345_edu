# TeamChallenge.io_1345_edu
Team Challenge project #1345. Test and education with git. Any action from co-owners.

## First run:

<img width="1084" alt="Знімок екрана 2025-01-14 о 21 34 43" src="https://github.com/user-attachments/assets/9bc20423-b21a-4a7a-9716-aaa72fe46481" />

## Added Swager Init page ...

<img width="1209" alt="Знімок екрана 2025-01-14 о 22 11 47" src="https://github.com/user-attachments/assets/94de68fa-05cf-41c1-90d3-9d00ae8dfd83" />

API /api/v1/cart GET example:
![Знімок екрана 2025-01-17 о 04 02 03](https://github.com/user-attachments/assets/b283d3a4-8474-4911-92cf-e91101c5b79e)


## API
### Cart 
/api/v1/cart
#### GET
```json
[
    {
        "product_id": 1,
        "product_name": "item1",
        "quantity": 4,
        "price": "100.00",
        "total_price": "400.00"
    },
    {
        "product_id": 2,
        "product_name": "item2",
        "quantity": 1,
        "price": "200.00",
        "total_price": "200.00"
    }
]
```
#### POST
```json
{
 "product_id": 1,
 "quantity": 1,
 "price": 100.00
}
```
#### DELETE
Can delete one product:
```json
{"product_id": 1}
```
Or without any data can delete all item's cart

#### Example of GET

![Знімок екрана 2025-01-17 о 03 44 43](https://github.com/user-attachments/assets/00625509-803a-487e-aed3-8bf183ed5143)

