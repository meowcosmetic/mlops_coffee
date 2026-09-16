async def test_create_and_list_prompt_versions(client):
    resp = await client.post("/api/prompts", json={
        "name": "drink-assistant-system", "version": "1.2.0", "template": "New template {name}",
    })
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["version"] == "1.2.0"
    assert created["is_active"] is False

    listing = await client.get("/api/prompts", params={"name": "drink-assistant-system"})
    assert listing.status_code == 200
    versions = {v["version"] for v in listing.json()}
    assert {"1.1.0", "1.2.0"} <= versions


async def test_activate_prompt_version_switches_active_row(client):
    created = (await client.post("/api/prompts", json={
        "name": "drink-assistant-system", "version": "1.2.0", "template": "New template {name}",
    })).json()

    activated = await client.post(f"/api/prompts/{created['id']}/activate")
    assert activated.status_code == 200
    assert activated.json()["is_active"] is True

    listing = (await client.get("/api/prompts", params={"name": "drink-assistant-system"})).json()
    active_versions = [v["version"] for v in listing if v["is_active"]]
    assert active_versions == ["1.2.0"]
