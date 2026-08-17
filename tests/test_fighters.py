def test_read_root(client):
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_get_nonexistent_fighter(client):
    response = client.get("/api/fighters/999999")
    assert response.status_code == 404
