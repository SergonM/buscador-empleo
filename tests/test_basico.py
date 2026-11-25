"""Pruebas rápidas: python -m unittest discover tests"""
import json
import unittest
from datetime import date
from pathlib import Path

from buscador.filtros import deduplicar, motivo_descarte
from buscador.fuentes.getonboard import _a_oferta
from buscador.pagina import generar
from buscador.ranking import puntuar
from buscador.texto import anios_experiencia, normalizar

PERFIL = json.loads((Path(__file__).resolve().parent.parent / "perfil.json").read_text(encoding="utf-8"))


def item(titulo, sen=2, rm="fully_remote", paises=("Remote",), desc="", id_=1):
    return {
        "id": id_, "type": "job",
        "attributes": {
            "title": titulo, "description": desc, "remote_modality": rm, "countries": list(paises),
            "seniority": {"data": {"id": sen, "type": "seniority"}}, "published_at": 1795000000,
            "company": {"data": {"id": "acme", "attributes": {"name": "Acme"}}},
        },
        "links": {"public_url": f"https://www.getonbrd.com/jobs/{id_}"},
    }


class Pruebas(unittest.TestCase):
    def o(self, *a, **k):
        return _a_oferta(item(*a, **k))

    def test_normalizar_y_anios(self):
        self.assertEqual(normalizar("<p>Analítica  Á</p>"), "analitica a")
        self.assertEqual(anios_experiencia(normalizar("Al menos 3 años de experiencia en SQL")), 3)
        self.assertEqual(anios_experiencia(normalizar("1-2 years of experience")), 1)
        self.assertIsNone(anios_experiencia("sin experiencia previa"))

    def test_pasa_junior_remoto(self):
        self.assertIsNone(motivo_descarte(self.o("Data Analyst Junior"), PERFIL))
        self.assertIsNone(motivo_descarte(self.o("Analista GRC", paises=["Colombia"], rm="hybrid", desc="Bogotá"), PERFIL))

    def test_descarta(self):
        self.assertIn("senior", motivo_descarte(self.o("Senior Data Engineer"), PERFIL))
        self.assertIn("nivel", motivo_descarte(self.o("Data Analyst", sen=4), PERFIL))
        self.assertIsNone(motivo_descarte(self.o("Data Analyst", sen=3), PERFIL))
        self.assertIn("años", motivo_descarte(self.o("Data Analyst", desc="5 años de experiencia"), PERFIL))
        self.assertIn("ubicación", motivo_descarte(self.o("Analista de datos", rm="no_remote", paises=["Chile"]), PERFIL))
        self.assertIn("ubicación", motivo_descarte(self.o("Analista de datos", rm="hybrid", paises=["Colombia"], desc="Sede Medellín"), PERFIL))
        self.assertIn("áreas", motivo_descarte(self.o("Desarrollador Frontend Junior"), PERFIL))

    def test_dedup_y_ranking(self):
        a, b = self.o("Data Analyst Jr", id_=1), self.o("Data Analyst Jr", id_=2)
        self.assertEqual(len(deduplicar([a, b])), 1)
        r = puntuar(self.o("Analista de Compliance Junior", desc="SQL, Python, ISO 27001, sector salud"), PERFIL, date(2026, 11, 20))
        self.assertGreater(r["puntaje"], 60)
        self.assertIn("Ciberseguridad / GRC", r["por_que"])

    def test_pagina(self):
        o = puntuar(self.o("Data Analyst Jr </script>"), PERFIL)
        o.update(nueva=True)
        html = generar([o], {"actualizado": "2026-11-25T12:00+00:00", "nuevas": 1, "mostradas": 1, "revisadas": 5, "fuentes": ["GetOnBoard"]})
        self.assertNotIn("Jr </script>", html)

    def test_linkedin_indeed(self):
        from buscador.fuentes.linkedin_indeed import _a_oferta as li
        o = li({"site": "linkedin", "id": "li-1", "title": "Analista de Datos Junior", "company": "Bancolombia",
                "location": "Bogotá, D.C., Colombia", "date_posted": date(2026, 11, 24), "is_remote": float("nan"),
                "description": "Modelo híbrido. SQL y Power BI", "job_url": "https://www.linkedin.com/jobs/view/1"})
        self.assertEqual(o["modalidad"], "Híbrido")
        self.assertEqual(o["fecha"], "2026-11-24")
        self.assertIsNone(motivo_descarte(o, PERFIL))
        med = li({"site": "indeed", "id": "in-2", "title": "Data Analyst", "company": "X", "location": "Medellín, Antioquia",
                  "job_url": "https://co.indeed.com/viewjob?jk=2", "description": ""})
        self.assertIn("ubicación", motivo_descarte(med, PERFIL))

    def test_remotos_zona(self):
        from buscador.fuentes.remotos import _zona_ok
        self.assertTrue(_zona_ok("LATAM"))
        self.assertTrue(_zona_ok("Worldwide"))
        self.assertFalse(_zona_ok("USA only"))


if __name__ == "__main__":
    unittest.main()
