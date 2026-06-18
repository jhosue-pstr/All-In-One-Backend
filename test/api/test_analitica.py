import pytest

SITE_ID = 1


class TestAnaliticaEndpoints:
    def test_registrar_visita(self, client):
        response = client.post(f"/api/modules/analitica/{SITE_ID}/visitas", json={
            "url": "/test-page",
            "titulo_pagina": "Test Page",
            "referer": "https://google.com",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["url"] == "/test-page"

    def test_registrar_visita_con_session(self, client):
        response = client.post(f"/api/modules/analitica/{SITE_ID}/visitas", json={
            "url": "/page",
            "session_id": "test-session-001",
        })
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_registrar_evento(self, client):
        response = client.post(f"/api/modules/analitica/{SITE_ID}/eventos", json={
            "tipo": "click",
            "etiqueta": "btn_test",
            "valor": "42",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_obtener_dashboard(self, client):
        response = client.get(f"/api/modules/analitica/{SITE_ID}/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "resumen" in data
        assert "visitas_por_dia" in data
        assert "top_paginas" in data
        assert "navegadores" in data
        assert "dispositivos" in data
        assert "ultimas_visitas" in data
        assert "eventos_recientes" in data
        assert data["resumen"]["visitas_hoy"] >= 0

    def test_obtener_dashboard_con_parametro_dias(self, client):
        response = client.get(f"/api/modules/analitica/{SITE_ID}/dashboard?dias=30")
        assert response.status_code == 200

    def test_registrar_evento_sin_auth_retorna_401(self, client):
        response = client.post(
            f"/api/modules/analitica/{SITE_ID}/eventos",
            json={"tipo": "click"},
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code in (401, 403)

    def test_obtener_dashboard_sin_auth_retorna_401(self, client):
        response = client.get(
            f"/api/modules/analitica/{SITE_ID}/dashboard",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code in (401, 403)
