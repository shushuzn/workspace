#!/usr/bin/env python3
"""
Materials Project API v2 Client
Using mp-api package (official)

Docs: https://docs.materialsproject.org
Install: pip install mp-api
"""

import os
from typing import List, Dict, Optional

# Try to import official mp-api package
try:
    from mp_api.client import MPRester
    MP_API_AVAILABLE = True
except ImportError:
    MP_API_AVAILABLE = False
    print("[WARNING] mp-api not installed. Install: pip install mp-api")

# Configuration
MP_API_KEY = os.getenv("MP_API_KEY")

if not MP_API_KEY:
    raise ValueError(
        "MP_API_KEY not found! Please set it in .env file or environment variable.\n"
        "Get your API key from: https://materialsproject.org/dashboard"
    )

print(f"[MP API] Connected with key: {MP_API_KEY[:10]}...")


class MaterialsProjectClient:
    """Materials Project API v2 Client (using mp-api)"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or MP_API_KEY

        if MP_API_AVAILABLE:
            self.mpr = MPRester(self.api_key)
            print("[MP API] Using official mp-api client")
        else:
            self.mpr = None
            print("[MP API] Using fallback HTTP client")

    def get_material_summary(self, material_id: str) -> Optional[Dict]:
        """Get material summary by ID (e.g., mp-1171422)"""
        if MP_API_AVAILABLE and self.mpr:
            try:
                # Use new API structure
                docs = self.mpr.materials.summary.search(material_ids=[material_id])
                if docs:
                    return docs[0].dict()
                return None
            except Exception as e:
                print(f"[MP API] Error: {e}")
                return None
        else:
            # Fallback: direct HTTP request
            import requests
            url = f"https://api.materialsproject.org/materials/{material_id}/summary"
            headers = {'X-API-KEY': self.api_key}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[MP API] HTTP Error: {response.status_code}")
                return None

    def search_by_formula(self, formula: str, limit: int = 10) -> List[Dict]:
        """Search materials by formula (e.g., LiFePO4, SiO2)"""
        if MP_API_AVAILABLE and self.mpr:
            try:
                # Use new API structure
                docs = self.mpr.materials.summary.search(formula=formula)
                results = []
                for doc in docs:
                    results.append(doc.dict())
                    if len(results) >= limit:
                        break
                return results
            except Exception as e:
                print(f"[MP API] Error: {e}")
                return []
        else:
            # Fallback: direct HTTP request
            import requests
            url = f"https://api.materialsproject.org/materials/search"
            headers = {'X-API-KEY': self.api_key}
            params = {'formula': formula, 'limit': limit}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                print(f"[MP API] HTTP Error: {response.status_code}")
                return []

    def get_band_structure(self, material_id: str) -> Optional[Dict]:
        """Get band structure for a material"""
        if MP_API_AVAILABLE and self.mpr:
            try:
                bs = self.mpr.bandstructure.get_bandstructure_by_material_id(material_id)
                return bs.dict() if bs else None
            except Exception as e:
                print(f"[MP API] Error: {e}")
                return None
        else:
            print("[MP API] Band structure requires mp-api package")
            return None

    def get_dos(self, material_id: str) -> Optional[Dict]:
        """Get density of states for a material"""
        if MP_API_AVAILABLE and self.mpr:
            try:
                dos = self.mpr.dos.get_dos_by_material_id(material_id)
                return dos.dict() if dos else None
            except Exception as e:
                print(f"[MP API] Error: {e}")
                return None
        else:
            print("[MP API] DOS requires mp-api package")
            return None

    def get_thermodynamics(self, material_id: str) -> Optional[Dict]:
        """Get thermodynamic properties"""
        if MP_API_AVAILABLE and self.mpr:
            try:
                thermo = self.mpr.thermo.get_thermo_by_material_id(material_id)
                return thermo.dict() if thermo else None
            except Exception as e:
                print(f"[MP API] Error: {e}")
                return None
        else:
            print("[MP API] Thermodynamics requires mp-api package")
            return None


def main():
    """Test the client"""
    print("=" * 60)
    print("Materials Project API v2 Client")
    print("=" * 60)

    client = MaterialsProjectClient()

    # Test search
    print("\n[1/2] Searching for LiFePO4...")
    results = client.search_by_formula("LiFePO4", limit=3)

    if results:
        print(f"Found {len(results)} materials:")
        for mat in results:
            if isinstance(mat, dict):
                mat_id = mat.get('material_id', mat.get('materialId', 'N/A'))
                formula = mat.get('formula', {}).get('pretty', 'N/A') if isinstance(mat.get('formula'), dict) else mat.get('formula', 'N/A')
                print(f"  - {mat_id}: {formula}")

    # Test material summary (use LiFePO4 from search results)
    print("\n[2/2] Getting material details...")
    if results:
        first_mat_id = results[0].get('material_id', 'mp-dqobo')
        summary = client.get_material_summary(first_mat_id)

        if summary:
            print(f"Material: {first_mat_id}")
            formula = summary.get('formula', {})
            if isinstance(formula, dict):
                print(f"  Formula: {formula.get('pretty', 'N/A')}")
            else:
                print(f"  Formula: {formula}")
            print(f"  Energy: {summary.get('formation_energy_per_atom', 'N/A')} eV/atom")
            print(f"  Band Gap: {summary.get('band_gap', 'N/A')} eV")
        else:
            print(f"No details for {first_mat_id}")

    print("\n" + "=" * 60)
    print("API client ready!")
    print("=" * 60)

    if not MP_API_AVAILABLE:
        print("\n[INFO] For full functionality, install mp-api:")
        print("  pip install mp-api")


if __name__ == '__main__':
    main()
