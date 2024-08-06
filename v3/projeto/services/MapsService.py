class MapsService:
    def getDirections(self, startLat, startLon, endLat, endLon):
        # Lógica para obter direções
        return {'error': 'Direções não suportadas por Nominatim'}

    def getMapImage(self, centerLat, centerLon):
        staticMapUrl = f"https://staticmap.openstreetmap.de/staticmap.php?center={centerLat},{centerLon}&zoom=13&size=600x300"
        return staticMapUrl
