"""Tests for POST /api/v1/herbs/import — CSV bulk import."""

import io

from httpx import AsyncClient

API = "/api/v1/herbs/import"


def _csv_bytes(rows: list[list[str]]) -> bytes:
    """Build CSV content from header + data rows and return as UTF-8 bytes."""
    header = ["name_cn", "name_pinyin", "category", "nature", "flavor", "efficacy"]
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(row))
    return "\n".join(lines).encode("utf-8")


def _csv_file(rows: list[list[str]], filename: str = "herbs.csv"):
    """Return an httpx-compatible ``files`` dict for multipart upload."""
    content = _csv_bytes(rows)
    return {"file": (filename, content, "text/csv")}


# ---- happy-path --------------------------------------------------------


async def test_import_csv_success(auth_client: AsyncClient):
    rows = [
        ["白术", "Bai Zhu", "补气药", "温", "甘|苦", "健脾益气"],
        ["茯苓", "Fu Ling", "利水渗湿药", "平", "甘|淡", "利水渗湿"],
    ]
    resp = await auth_client.post(API, files=_csv_file(rows))
    assert resp.status_code == 200
    body = resp.json()
    assert body["success_count"] == 2
    assert body["error_count"] == 0
    assert body["errors"] == []


async def test_import_csv_duplicate(auth_client: AsyncClient):
    rows = [
        ["川芎", "Chuan Xiong", "活血药", "温", "辛", "活血行气"],
    ]
    # First import should succeed.
    resp1 = await auth_client.post(API, files=_csv_file(rows))
    assert resp1.status_code == 200
    assert resp1.json()["success_count"] == 1

    # Second import with same name_cn should report duplicate.
    resp2 = await auth_client.post(API, files=_csv_file(rows))
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["success_count"] == 0
    assert body["error_count"] == 1
    assert "Duplicate" in body["errors"][0]["error"]


async def test_import_csv_missing_name(auth_client: AsyncClient):
    rows = [
        ["", "Kong", "未分类", "", "", ""],  # empty name_cn
    ]
    resp = await auth_client.post(API, files=_csv_file(rows))
    assert resp.status_code == 200
    body = resp.json()
    assert body["error_count"] == 1
    assert body["success_count"] == 0
    assert "name_cn" in body["errors"][0]["error"].lower()


async def test_import_csv_flavor_pipe_separator(auth_client: AsyncClient):
    rows = [
        ["丹参", "Dan Shen", "活血药", "微寒", "甘|苦", "活血祛瘀"],
    ]
    resp = await auth_client.post(API, files=_csv_file(rows))
    assert resp.status_code == 200
    assert resp.json()["success_count"] == 1

    # Verify the flavors were correctly parsed into a list.
    get_resp = await auth_client.get("/api/v1/herbs", params={"q": "丹参"})
    assert get_resp.status_code == 200
    items = get_resp.json()["items"]
    assert len(items) >= 1
    herb = items[0]
    assert set(herb["flavor"]) == {"甘", "苦"}


# ---- auth / validation -------------------------------------------------


async def test_import_csv_unauthenticated(client: AsyncClient):
    rows = [["测试", "Ce Shi", "未分类", "", "", ""]]
    resp = await client.post(API, files=_csv_file(rows))
    assert resp.status_code in (401, 403)


async def test_import_non_csv_file(auth_client: AsyncClient):
    bad_file = {"file": ("data.txt", b"not,csv,content", "text/plain")}
    resp = await auth_client.post(API, files=bad_file)
    assert resp.status_code == 400
