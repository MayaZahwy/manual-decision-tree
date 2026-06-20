# Dataset Schema

The training CSV must include these columns:

| Column   | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| Sleep    | number | Average sleep hours per night                    |
| Meetings | number | Number of calls or meetings per day              |
| Weekends | YES/NO | Whether the developer works on weekends          |
| Stress   | number | Subjective stress level from 1 to 10             |
| Target   | text   | Burnout class label                              |

## Allowed Target values

- `healthy`
- `risk of burnout`
- `vacation required`
- `critical condition`

## Example rows

```csv
Sleep,Meetings,Weekends,Stress,Target
8,2,NO,3,healthy
6,6,YES,7,risk of burnout
5,8,YES,9,vacation required
4,9,YES,10,critical condition
```

Create your own CSV file with this format and upload it via `POST /train` or the dashboard **Train Model** section.

A sample dataset with 25 rows is committed at [backend/data/sample_burnout.csv](../data/sample_burnout.csv).
