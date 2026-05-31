from Repository import SensorRepository
from Analyzer import CO2Analyzer

repo = SensorRepository()
repo.load_csv("dataset/data_.csv")

data_sensor = repo.get_all()

print(CO2Analyzer(data_sensor).analyze())