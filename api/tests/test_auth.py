"""Tests for API key authentication middleware."""

import pytest


@pytest.mark.asyncio
async def test_missing_api_key_returns_401(client):
    resp = await client.get("/api/overview", headers={"X-API-Key": ""})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_wrong_api_key_returns_401(client):
    resp = await client.get("/api/overview", headers={"X-API-Key": "wrong-key"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_valid_api_key_returns_200(client):
    resp = await client.get("/api/overview")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_no_auth_required(client):
    resp = await client.get("/api/health", headers={})
    assert resp.status_code == 200
