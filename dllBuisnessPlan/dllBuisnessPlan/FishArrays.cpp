#include <stdio.h>
#include <math.h>


extern "C" __declspec(dllexport) float update_biomass(
	float* fishArray,
	int amountFish
)
{
	float biomass = 0.0;

	for (int i = 0; i < amountFish; i++) {
		biomass += fishArray[i];
	}

	biomass = biomass / 1000;
	return biomass;
}


extern "C" __declspec(dllexport) float _calculation_daily_growth(
	float previousMass,
	float massAccumulationCoefficient,
	float* biomass
)
{
	float y = 1.0 / 3.0;
	float x = powf(previousMass, y);
	float newMass = x + (massAccumulationCoefficient / 3);
	newMass = powf(newMass, 3);
	*biomass += (newMass - previousMass) / 1000;
	return newMass;
}


extern "C" __declspec(dllexport) float _determination_total_daily_weight_feed(
	float previousMass,
	float currentMass,
	float feedRatio
)
{
	float relativeGrowth = (float(currentMass) - float(previousMass))
		/ float(previousMass);
	float result = previousMass * relativeGrowth * feedRatio;
	return result;
}


extern "C" __declspec(dllexport) float daily_work(
	float* arrayMass,
	float* arrayMassAccumulationCoefficient,
	int amountFish,
	float feedRatio,
	float* biomass
)
{
	// ежедневная масса корма
	float dailyFeedMass = 0.0;
	float previousMass = 0.0;

	for (int i = 0; i < amountFish; i++) {
		previousMass = arrayMass[i];
		// изменяем массу рыбки
		arrayMass[i] = _calculation_daily_growth(
			arrayMass[i],
			arrayMassAccumulationCoefficient[i],
			biomass);
		// расчитываем массу корма на сегодняшний день
		dailyFeedMass += _determination_total_daily_weight_feed(
			previousMass,
			arrayMass[i],
			feedRatio
		);
	}
	//printf("Daily_work works!\n");

	dailyFeedMass = dailyFeedMass / 1000;
	return dailyFeedMass;
}


extern "C" __declspec(dllexport) float do_daily_work_some_days
(
	float* arrayMass,
	float* arrayMassAccumulationCoefficient,
	int amountFish,
	float feedRatio,
	float* biomass,
	int amountDays
)
{
	float totalFeedMass = 0.0;
	for (int i = 0; i < amountDays; i++) {
		totalFeedMass += daily_work(arrayMass, arrayMassAccumulationCoefficient,
			amountFish, feedRatio, biomass);

	}
	return totalFeedMass;
}


extern "C" __declspec(dllexport) int calculate_when_fish_will_be_sold
(
	float* arrayMass,
	float* arrayMassAccumulationCoefficient,
	int amountFish,
	float feedRatio,
	float* biomass,
	float massComercialFish,
	int packageValue
)
{
	int amountDays = 0;
	int amountSoldFish = 0;

	// будем делать ежедневную работу, пока не врастим минимальное оличство рыбы или всю рыбу
	while ((amountSoldFish < packageValue) && (amountSoldFish != amountFish))
	{
		daily_work(arrayMass, arrayMassAccumulationCoefficient,
			amountFish, feedRatio, biomass);
		// проверяем, выросло ли достаточно рыбы
		amountSoldFish = 0;
		for (int i =0; i < amountFish; i++) 
		{
			if (arrayMass[i] >= massComercialFish) amountSoldFish++;
		}
		// увелииваем день
		amountDays++;
	}
	// возвращаем количество дней, необходимое для выращивания данной рыбы
	return amountDays;
}


extern "C" __declspec(dllexport) int calculate_when_density_reaches_limit
(
	float* arrayMass,
	float* arrayMassAccumulationCoefficient,
	int amountFish,
	float feedRatio,
	float* biomass,
	float maxDensity,
	float square
)
{
	int amountDays = 0;
	float currentDensity = *biomass / square;

	while (currentDensity < maxDensity) 
	{
		daily_work(arrayMass, arrayMassAccumulationCoefficient,
			amountFish, feedRatio, biomass);
		currentDensity = *biomass / square;
		amountDays++;
	}
	return amountDays;
}
