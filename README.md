```python
api = SCB(version)

api.parameters() # api.list()

parameter = api.parameter(1)

parameter.id # =key
# 1

parameter.updated
# updated

parameter.label
#

parameter.description
# u"momentanvärde, 1 gång/tim"

parameter.dimensions()
# [<Dimension: Station>, <Dimension: Parameter>, <Dimension: Timepoint>]

stations = parameter.dimension("station")
# <Dimension: Station>

station = stations.get("Abelvattnet")

station.id
station.label
station.height
station.latitude
station.longitude

parameter.query(station=["Abelvattnet"], period=["latest-hour"])
```
