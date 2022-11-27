import numpy as np
import matplotlib.pyplot as plt
import datetime as date
import copy
from ctypes import *


class DistributionParameters():
    # среднеквадратичное отклонение
    scale = 0
    # средний коэффициент массонакопления
    massAccumulationCoefficient = 0
    # количество рыб
    amountFishes = 0
    # массив значений, которые распределены по Гауссу в заданных параметрах
    _gaussValues = []

    def __init__(self, amountFishes,
                 scale=0.003,
                 massAccumulationCoefficientMin=0.07,
                 massAccumulationCoefficientMax=0.087):
        self.massAccumulationCoefficient = (massAccumulationCoefficientMin +
                                       massAccumulationCoefficientMax) / 2
        self.amountFishes = amountFishes
        self.scale = scale
        self._make_gaussian_distribution()

    def _make_gaussian_distribution(self):
        self._gaussValues = np.random.normal(self.massAccumulationCoefficient,
                                        self.scale,
                                        self.amountFishes)
        self._gaussValues.sort()

    def draw_hist_distribution(self, numberFishInOneColumn):
        plt.hist(self._gaussValues, numberFishInOneColumn)
        plt.show()

    def return_array_distributed_values(self):
        return self._gaussValues


def assemble_array(array, amountItems, index):
    result = (c_float * amountItems)()
    for i in range(amountItems):
        result[i] = array[i][index]
    return result


class FishArray():
    _amountFishes = 0
    _arrayFishes = list()
    _biomass = c_float()
    # массив покупок мальков
    _arrayFryPurchases = list()
    _feedRatio = 1.5
    _dllBuisnessPlan = 0


    def __init__(self, feedRatio=1.5):
        self._feedRatio = c_float(feedRatio)
        self._biomass = c_float()
        self._amountFishes = 0
        self._arrayFishes = list()
        self._arrayFryPurchases = list()
        self._dllBuisnessPlan = WinDLL('D:/github/buisnessPlan_v1.2.1/buisnessPlan_v1.2/dllBuisnessPlan/x64/Debug/dllBuisnessPlan.dll')

    def add_biomass(self, date, amountFishes, averageMass):
        # создаем параметры для нормального распределения коэффициентов массонакопления
        distributionParameters = DistributionParameters(amountFishes)
        arrayCoefficients = distributionParameters.return_array_distributed_values()

        # закидываем информацию о новой биомассе в массив
        for i in range(amountFishes):
            # ноль означает (количество дней в бассике, но это не точно
            # arrayFishes = [[startingMass, massAccumulationCoefficient, currentMass],...]
            self._arrayFishes.append([averageMass, arrayCoefficients[i], averageMass])
            self._arrayFryPurchases.append([date, amountFishes, averageMass])

        # увеличиваем количество рыбы в бассейне
        self._amountFishes += amountFishes
        # так как все в граммах, то делим на 1000, чтобы получить килограммы в биомассе
        self._biomass.value += amountFishes * averageMass / 1000

    # функция добавляет уже немного подросшие рыбки из других бассейнов
    def add_other_FishArrays(self, fishArray):
        amountNewFishes = len(fishArray)

        # arrayFishes = [[startingMass, massAccumulationCoefficient, currentMass]
        for i in range(amountNewFishes):
            self._biomass = self._biomass + fishArray[i][2] / 1000
            self._arrayFishes.append(fishArray[i])
        self._amountFishes += amountNewFishes

    def remove_biomass(self, indexes, amountIndexes):
        removedFishes = list()
        for i in range(amountIndexes):
            if (indexes[i]):
                fish = self._arrayFishes.pop(i)
                removedFishes.append(fish)
                # уменьшаем количество рыб
                self._amountFishes -= 1
                # уменьшаем биомассу
                self._biomass.value -= fish[2] / 1000
        return removedFishes

    def update_biomass(self):
        arrayMasses = assemble_array(self._arrayFishes, self._amountFishes, 2)
        upBioM = self._dllBuisnessPlan.update_biomass
        upBioM.argtypes = [POINTER(c_float), c_int]
        upBioM.restype = c_float
        self._biomass.value = upBioM(arrayMasses, self._amountFishes)

    def daily_work(self):
        # подготовим переменные для использования ctypes
        dailyWorkLib = self._dllBuisnessPlan.daily_work

        dailyWorkLib.argtypes = [POINTER(c_float), POINTER(c_float),
                                 c_int, c_float, POINTER(c_float)]
        dailyWorkLib.restype = c_float

        # соберем массивы масс и коэффициентов массонакопления
        arrayMass = assemble_array(self._arrayFishes, self._amountFishes, 2)
        arrayMassAccumulationCoefficient = assemble_array(self._arrayFishes,
                                                          self._amountFishes, 1)

        dailyFeedMass = dailyWorkLib(arrayMass, arrayMassAccumulationCoefficient,
                                     self._amountFishes, self._feedRatio,
                                     byref(self._biomass))

        for i in range(self._amountFishes):
            self._arrayFishes[i][2] = arrayMass[i]

        return dailyFeedMass

    def do_daily_work_some_days(self, amountDays):
        # подготовим переменные для использования ctypes
        dailyWorkLib = self._dllBuisnessPlan.do_daily_work_some_days

        dailyWorkLib.argtypes = [POINTER(c_float), POINTER(c_float),
                                 c_int, c_float, POINTER(c_float), c_int]
        dailyWorkLib.restype = c_float

        # соберем массивы масс и коэффициентов массонакопления
        arrayMass = assemble_array(self._arrayFishes, self._amountFishes, 2)
        arrayMassAccumulationCoefficient = assemble_array(self._arrayFishes,
                                                          self._amountFishes, 1)

        totalFeedMass = dailyWorkLib(arrayMass, arrayMassAccumulationCoefficient,
                                     self._amountFishes, self._feedRatio,
                                     byref(self._biomass), amountDays)

        for i in range(self._amountFishes):
            self._arrayFishes[i][2] = arrayMass[i]

        return totalFeedMass

    def print_array_fishes(self):
        print('biomass = ', self._biomass.value)
        print(self._arrayFishes)

    def get_biomass(self):
        return self._biomass.value

    def get_amount_fishes(self):
        return self._amountFishes

    def get_array_fish(self):
        return self._arrayFishes

    def calculate_when_fish_will_be_sold(self, massComercialFish,
                                         singleVolume):
        # подготовим переменные для использования ctypes
        calculateLib = self._dllBuisnessPlan.calculate_when_fish_will_be_sold

        calculateLib.argtypes = [POINTER(c_float), POINTER(c_float),
                                 c_int, c_float, POINTER(c_float),
                                 c_float, c_int]
        calculateLib.restype = c_int

        # соберем массивы масс и коэффициентов массонакопления
        arrayMass = assemble_array(self._arrayFishes, self._amountFishes, 2)
        arrayMassAccumulationCoefficient = assemble_array(self._arrayFishes,
                                                          self._amountFishes, 1)

        amountDays = calculateLib(arrayMass, arrayMassAccumulationCoefficient,
                                     self._amountFishes, self._feedRatio,
                                     byref(self._biomass), massComercialFish,
                                  singleVolume)

        for i in range(self._amountFishes):
            self._arrayFishes[i][2] = arrayMass[i]

        return amountDays

    def calculate_when_density_reaches_limit(self, maxDensity, square):
        # подготовим переменные для использования ctypes
        calculateLib = self._dllBuisnessPlan.calculate_when_density_reaches_limit

        calculateLib.argtypes = [POINTER(c_float), POINTER(c_float),
                                 c_int, c_float, POINTER(c_float),
                                 c_float, c_float]
        calculateLib.restype = c_int

        # соберем массивы масс и коэффициентов массонакопления
        arrayMass = assemble_array(self._arrayFishes, self._amountFishes, 2)
        arrayMassAccumulationCoefficient = assemble_array(self._arrayFishes,
                                                          self._amountFishes, 1)

        amountDays = calculateLib(arrayMass, arrayMassAccumulationCoefficient,
                                     self._amountFishes, self._feedRatio,
                                     byref(self._biomass), maxDensity,
                                  square)

        for i in range(self._amountFishes):
            self._arrayFishes[i][2] = arrayMass[i]

        return amountDays


class Pool():
    square = 0
    maxPlantingDensity = 0
    arrayFishes = 0
    # количество мальков в 1 упаковке
    singleVolumeFish = 0
    # цена на мальков
    costFishFry = [[5, 35],
                   [10, 40],
                   [20, 45],
                   [30, 50],
                   [50, 60],
                   [100, 130]]
    # массив, в котором хранится информация о покупке мальков
    arrayFryPurchases = list()
    # массив, в котором хранится информация о продаже рыбы
    arraySoldFish = list()
    # текущая плотность посадки
    currentDensity = 0
    # массив кормежек
    feeding = list()
    # масса товарной рыбы
    massComercialFish = 350
    # библиотека на си для работы с этим с классом
    _dllPool = 0
    # цена рыбы
    price = 1000


    def __init__(self, square, singleVolumeFish=1, price=1000,
                 massComercialFish=350,
                 maximumPlantingDensity=40):
        self.square = square
        self.massComercialFish = massComercialFish
        self.maxPlantingDensity = maximumPlantingDensity
        self.singleVolumeFish = singleVolumeFish
        self.arrayFishes = FishArray()
        self.feeding = list()
        self.arrayFryPurchases = list()
        self.price = price
        self._dllPool = WinDLL("D:/github/buisnessPlan_v1.2.1/buisnessPlan_v1.2/dllPool/x64/Debug/dllPool.dll")

    def add_new_biomass(self, amountFishes, averageMass, date):
        self.arrayFishes.add_biomass(date, amountFishes, averageMass)
        # сохраним инфо о покупки мальков
        # arrayFryPurchases[i] = [date, amountFries, averageMass, totalPrice]
        totalPrice = 0
        for i in range(len(self.costFishFry)):
            if (averageMass < self.costFishFry[i][0]):
                totalPrice = amountFishes * self.costFishFry[i][1]
        self.arrayFryPurchases.append([date, amountFishes, averageMass, totalPrice])
        self.currentDensity = amountFishes * (averageMass / 1000) / self.square

    def daily_growth(self, day):
        todayFeedMass = self.arrayFishes.daily_work()
        # сохраняем массы кормежек
        self.feeding.append([day, todayFeedMass])

        # проверяем, есть ли переизбыток
        self.currentDensity = self.arrayFishes.get_biomass() / self.square
        if (self.currentDensity >= self.maxPlantingDensity):
            isThereOverabundanceFish = True
        else:
            isThereOverabundanceFish = False

        self.has_there_been_enough_fish_sale(day)

    # функция будет возвращать, выросло ли достаточно рыбы на продажу
    def has_there_been_enough_fish_sale(self, day):
        # подготовка для использования dllPool
        checkingGrownFishLib = self._dllPool.has_there_been_enough_fish_sale
        checkingGrownFishLib.argtypes = [POINTER(c_float), c_int,
                                         c_float, c_int, POINTER(c_bool)]
        checkingGrownFishLib.restypes = c_bool

        amountFishes = self.arrayFishes.get_amount_fishes()
        arrayMass = assemble_array(self.arrayFishes.get_array_fish(),
                                   amountFishes,
                                   2)
        indexes = (c_bool * amountFishes)(False)
        # проверяем, есть ли подросшие рыбки
        flag = checkingGrownFishLib(arrayMass, amountFishes, self.massComercialFish,
                                    self.singleVolumeFish, indexes)

        # если функция выдала True, то есть рыба на продажу
        if (flag):
            soldFish = self.arrayFishes.remove_biomass(indexes, amountFishes)
            # продаем выросшую рыбу и сохраняем об этом инфу
            soldBiomass = 0
            amountSoldFish = 0
            for i in range(len(soldFish)):
                soldBiomass += soldFish[i][2] / 1000
                amountSoldFish += 1
            revenue = soldBiomass * self.price

            self.arraySoldFish.append([day, amountSoldFish, soldBiomass, revenue])
            # обновим density
            self.currentDensity = self.arrayFishes.get_biomass() / self.square

    def update_density(self):
        self.currentDensity = self.arrayFishes.get_biomass() / self.square

    def calculate_when_fishArray_will_be_sold(self):
        testFishArray = copy.deepcopy(self.arrayFishes)
        amountDays = testFishArray.calculate_when_fish_will_be_sold(self.massComercialFish,
                                                                self.singleVolumeFish)
        return [amountDays, testFishArray.get_biomass()]

    def calculate_when_density_reaches_limit(self):
        testFishArray = copy.deepcopy(self.arrayFishes)
        amountDays = testFishArray.calculate_when_density_reaches_limit(self.maxPlantingDensity,
                                                                        self.square)
        testCurrentDensity = testFishArray.get_biomass() / self.square

        return [amountDays, testFishArray.get_biomass(), testCurrentDensity]


class CWSD():
    amountPools = 0
    amountGroups = 0
    # температура воды
    temperature = 21
    # арендная плата
    rent = 70000
    # стоимость киловатт в час
    costElectricityPerHour = 3.17
    # мощность узв
    equipmentCapacity = 5.6
    # стоимость корма
    feedPrice = 260
    onePoolSquare = 0
    pools = list()
    profit = list()

    def __init__(self, poolSquare, amountPools=8, amountGroups=4, fishPrice=1000,
                 feedPrice=260, equipmentCapacity=5.5, rent=70000,
                 costElectricityPerHour=3.17, temperature=21):
        self.onePoolSquare = poolSquare
        self.amountGroups = amountGroups
        self.amountPools = amountPools
        self.fishPrice = fishPrice
        self.temperature = temperature
        self.rent = rent
        self.costElectricityPerHour = costElectricityPerHour
        self.equipmentCapacity = equipmentCapacity
        self.feedPrice = feedPrice
        self.pools = list()
        self.profit = list()

        for i in range(amountPools):
            pool = Pool(poolSquare)
            self.pools.append(pool)

    def add_biomass_in_pool(self, poolNumber, amountFishes, mass, date):
        self.pools[poolNumber].add_new_biomass(amountFishes, mass, date)

    def _calculate_technical_costs(self, startingDate, endingDate):
        deltaTime = endingDate - startingDate
        amountDays = deltaTime.days
        electrisityCost = amountDays * 24 * self.equipmentCapacity * self.costElectricityPerHour
        rentCost = (int(amountDays / 30)) * self.rent
        return [rentCost, electrisityCost, rentCost + electrisityCost]

    def _calculate_biological_costs(self, startingDate, endingDate):
        day = startingDate
        feedMass = 0
        fryCost = 0

        while(day < endingDate):
            for i in range(self.amountGroups):
                # подсчет затрат на корма
                startingDayInThisPool = self.pools[i].feeding[0][0]
                if (day >= startingDayInThisPool):
                    amountDaysFeedingInThisPool = (day - startingDayInThisPool).days
                    feedMass += self.pools[i].feeding[amountDaysFeedingInThisPool][1]

                # подсчет затрат на мальков.
                for j in range(len(self.pools[i].arrayFryPurchases)):
                    if (day == self.pools[i].arrayFryPurchases[j][0]):
                        fryCost += self.pools[i].arrayFryPurchases[j][3]
                    elif (day > self.pools[i].arrayFryPurchases[j][0]):
                        break
            day += date.timedelta(1)

        feedCost = feedMass * self.feedPrice
        return [feedCost, fryCost, feedCost + fryCost]


class Opimization():
    def calculate_optimized_amount_fish(self, amountDays, startAmount, step,
                                        averageMass, square, maxDensity):
        amountFish = startAmount
        currentDensity = 0

        while(currentDensity <= maxDensity):
            testPool = Pool(square, 10, 1000, 350, maxDensity)
            testPool.add_new_biomass(amountFish, averageMass, date.date.today())


# проверка Pool
'''
x = Pool(5)
x.add_new_biomass(1, 50, date.date.today())
x.add_new_biomass(1, 100, date.date.today())
x.add_new_biomass(1, 340, date.date.today())

amountDays = 10
day = date.date.today()
for i in range(amountDays):
    x.daily_growth(day)
    day += date.timedelta(1)
    print(x.arrayFishes.get_amount_fishes())
'''

# проверка fishArray и fishArray.daily_work()
'''
x = FishArray()
x.add_biomass(date.date.today(), 5, 10)

x.add_biomass(date.date.today(), 5, 200)

amountDays = 10
feedMass = 0
for i in range(amountDays):
    feedMass += x.daily_work()
x.update_biomass()
print('feedMass = ', feedMass)
x.print_array_fishes()
'''

# проверка do_daily_work_some_days
'''
x = FishArray()
x.add_biomass(date.date.today(), 5, 10)
x.add_biomass(date.date.today(), 5, 200)

y = FishArray()
y.add_biomass(date.date.today(), 5, 10)
y.add_biomass(date.date.today(), 5, 200)

amountDays = 10
feedMassY = 0
feedMassX = x.do_daily_work_some_days(amountDays)

for i in range(amountDays):
    feedMassY += y.daily_work()

x.update_biomass()
print('feedMass = ', feedMassX)
x.print_array_fishes()

y.update_biomass()
print('feedMass = ', feedMassY)
y.print_array_fishes()
'''

# проверка calculate_when_fish_will_be_sold
'''
x = Pool(5, 2)
x.add_new_biomass(3, 300, date.date.today())
x.arrayFishes.print_array_fishes()
result = x.calculate_when_fishArray_will_be_sold()
x.arrayFishes.print_array_fishes()
amountDays = result[0]
print(result)

day = date.date.today()
for i in range(amountDays):
    x.arrayFishes.daily_work()
x.arrayFishes.print_array_fishes()
'''

# проверка calculate_when_density_reaches_limit
'''
x = Pool(5, 2)
x.add_new_biomass(3, 300, date.date.today())
x.arrayFishes.print_array_fishes()

result = x.calculate_when_density_reaches_limit()
print(result)

for i in range(result[0]):
    x.arrayFishes.daily_work()

x.update_density()
print([x.arrayFishes.get_biomass(), x.currentDensity])
'''


