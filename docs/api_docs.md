# API DOCS

## 공통 응답 규격
- 성공 응답 (단일)
```
{
  "status": "success",
  "result_code": 200,
  "result_msg": "요청이 처리되었습니다",
  "data": {
    "field": "value"
  }
}
```

- 성공 응답 리스트
```
{
  "status": "success",
  "result_code": 200,
  "result_msg": "검색 완료",
  "data": {
    "total": 50,
    "count": 10,
    "results": [...]
  }
}
```

- 에러 응답
```
{
  "status": "error",
  "result_code": 400,
  "result_msg": "잘못된 요청입니다"
}
```
