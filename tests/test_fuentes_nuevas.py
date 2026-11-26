"""Pruebas de las fuentes nuevas, el filtro de zonas remotas, las ayudas para postular y la página."""
import json
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from buscador.filtros import motivo_descarte
from buscador.fuentes import ats, remotos, workday
from buscador.pagina import archivos_pwa, generar
from buscador.ranking import puntuar

PERFIL = json.loads((Path(__file__).resolve().parent.parent / "perfil.json").read_text(encoding="utf-8"))


class Fuentes(unittest.TestCase):
    def test_greenhouse_filtra_ubicacion(self):
        data = {"jobs": [
            {"id": 1, "title": "Data Analyst Jr", "absolute_url": "https://x/1", "location": {"name": "Bogotá, Colombia"},
             "updated_at": "2026-11-20T10:00:00Z", "content": "&lt;p&gt;SQL y Python&lt;/p&gt;"},
            {"id": 2, "title": "Data Analyst", "absolute_url": "https://x/2", "location": {"name": "São Paulo"}},
        ]}
        with mock.patch.object(ats, "get_json", return_value=data):
            r = ats.greenhouse("sezzle", "Sezzle")
        self.assertEqual(len(r), 1)
        self.assertIn("Colombia", r[0]["paises"])
        self.assertIsNone(motivo_descarte(r[0], PERFIL))

    def test_lever_y_ashby(self):
        lv = [{"id": "a", "text": "Compliance Analyst", "hostedUrl": "https://l/a", "workplaceType": "remote",
               "categories": {"location": "LATAM"}, "createdAt": 1795000000000, "descriptionPlain": "1 year of experience"}]
        with mock.patch.object(ats, "get_json", return_value=lv):
            r = ats.lever("toptal", "Toptal")
        self.assertEqual(r[0]["modalidad"], "Remoto")
        self.assertIsNone(motivo_descarte(r[0], PERFIL))
        ab = {"jobs": [{"id": "z", "title": "Business Analyst", "jobUrl": "https://a/z", "location": "Bogotá",
                        "workplaceType": "Hybrid", "publishedAt": "2026-11-22T00:00:00Z", "descriptionPlain": "Excel"}]}
        with mock.patch.object(ats, "get_json", return_value=ab):
            r = ats.ashby("addi", "Addi")
        self.assertEqual(r[0]["modalidad"], "Híbrido")
        self.assertEqual(r[0]["fecha"], "2026-11-22")

    def test_remoto_de_otro_pais_no_sirve(self):
        base = dict(id="x", fuente="Lever", titulo="Data Analyst", empresa="A", url="u", remoto=True,
                    remote_modality="fully_remote", descripcion="")
        us = dict(base, paises=["Remote - US"], ubicacion="Remote - US")
        latam = dict(base, paises=["Remote - LATAM"], ubicacion="Remote - LATAM")
        solo = dict(base, paises=["Remote"], ubicacion="Remote")
        self.assertIn("ubicación", motivo_descarte(us, PERFIL))
        self.assertIsNone(motivo_descarte(latam, PERFIL))
        self.assertIsNone(motivo_descarte(solo, PERFIL))

    def test_workday(self):
        self.assertTrue(workday.pasa_titulo("Analyst Jr, Trade Compliance", PERFIL))
        self.assertFalse(workday.pasa_titulo("Sr Analyst Legal Template Transformation", PERFIL))
        self.assertFalse(workday.pasa_titulo("Sales Representative - Pasto", PERFIL))
        hoy = date(2026, 11, 26)
        self.assertEqual(workday._fecha_rel("Posted 5 Days Ago", hoy), "2026-11-21")
        self.assertEqual(workday._fecha_rel("Posted Today", hoy), "2026-11-26")

        def falso(url, cuerpo=None, intentos=3):
            if url.endswith("/jobs"):
                return {"total": 2, "jobPostings": [
                    {"title": "Data Analyst Jr", "externalPath": "/job/Bogota/Data-Analyst_R1", "postedOn": "Posted Today"},
                    {"title": "Senior Manager Finance", "externalPath": "/job/Bogota/Mgr_R2"}]}
            return {"jobPostingInfo": {"location": "Bogotá, Distrito Capital, Colombia", "jobDescription": "SQL, Power BI. Modelo híbrido",
                                       "startDate": "2026-11-25", "jobReqId": "R1", "externalUrl": "https://jj/R1"}}
        with mock.patch.object(workday, "_pedir", side_effect=falso), mock.patch.object(workday.time, "sleep"):
            r, _ = workday.buscar(["jj.wd5.myworkdayjobs.com jj JJ Johnson & Johnson"], PERFIL, hoy)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["empresa"], "Johnson & Johnson")
        self.assertEqual(r[0]["modalidad"], "Híbrido")
        self.assertIsNone(motivo_descarte(r[0], PERFIL))

    def test_jobicy_y_remoteok(self):
        jb = {"jobs": [{"id": 9, "jobTitle": "Junior Data Analyst", "companyName": "Z", "url": "https://j/9", "jobGeo": "LATAM",
                        "jobLevel": "Junior", "pubDate": "2026-11-24 10:00:00", "jobDescription": "SQL"},
                       {"id": 10, "jobTitle": "Analyst", "companyName": "Y", "url": "u", "jobGeo": "USA"}]}
        with mock.patch.object(remotos, "get_json", return_value=jb), mock.patch.object(remotos.time, "sleep"):
            r, _ = remotos.jobicy(["latam"])
        self.assertEqual([o["id"] for o in r], ["jobicy-9"])
        ro = [{"legal": "x"}, {"id": "1", "position": "Security Analyst", "company": "C", "location": "Worldwide", "date": "2026-11-25T00:00:00+00:00"},
              {"id": "2", "position": "Data Analyst", "company": "D", "location": "USA"}]
        with mock.patch.object(remotos, "get_json", return_value=ro):
            r, _ = remotos.remoteok()
        self.assertEqual([o["id"] for o in r], ["remoteok-1"])


class Ayudas(unittest.TestCase):
    def oferta(self, **k):
        base = dict(id="a", fuente="Workday", titulo="Analista de Compliance Junior", empresa="Johnson & Johnson", url="u",
                    modalidad="Híbrido", remoto=False, remote_modality="hybrid", paises=["Colombia"], ubicacion="Bogotá",
                    fecha="2026-11-25", seniority_id=None, seniority="", salario="",
                    descripcion="Buscamos recién egresado con conocimientos de SQL, Python, SAP e ISO 27001. Inglés intermedio. " * 20)
        base.update(k)
        return base

    def test_claves_idioma_calidad(self):
        o = puntuar(self.oferta(), PERFIL, date(2026, 11, 26))
        self.assertIn("sql", o["claves"])
        self.assertIn("sap", o["reforzar"])
        self.assertEqual(o["idioma"], "es")
        self.assertTrue(o["ingles"])
        self.assertGreaterEqual(o["calidad"], 60)
        self.assertIn("poca o ninguna experiencia", o["por_que"])
        en = puntuar(self.oferta(descripcion="You will work with the team and our stakeholders. Experience with SQL. " * 10), PERFIL)
        self.assertEqual(en["idioma"], "en")

    def test_conservada_mantiene_claves(self):
        o = puntuar(self.oferta(), PERFIL)
        o.pop("descripcion")
        claves = list(o["claves"])
        puntuar(o, PERFIL)
        self.assertEqual(o["claves"], claves)

    def test_pagina_y_pwa(self):
        o = puntuar(self.oferta(titulo="Data Analyst </script>"), PERFIL)
        o.update(nueva=True, visto="2026-11-26")
        o.pop("descripcion")
        html = generar([o], {"actualizado": "2026-11-26T12:00+00:00", "nuevas": 1, "mostradas": 1, "revisadas": 5,
                             "fuentes": ["Workday"], "estado_fuentes": {"Workday": {"ok": True, "ofertas": 1, "segundos": 3}}},
                       {"nombre": "Sergio González"})
        self.assertNotIn("Analyst </script>", html)
        self.assertIn("manifest.webmanifest", html)
        pwa = archivos_pwa()
        self.assertIn("icono-512.png", pwa["manifest.webmanifest"])
        self.assertIn("fetch", pwa["sw.js"])


if __name__ == "__main__":
    unittest.main()
