#include <stdio.h>
#include <math.h>


extern "C" __declspec(dllexport) int has_there_been_enough_fish_sale(
	float* arrayMass,
	int amountFish,
	float massComercialFish,
	int singleVolumeFish
)
{
	// количество выросших рыбок
	int numberGrowthFish = 0;
	for (int i = 0; i < amountFish; i++) {
		if (arrayMass[i] >= massComercialFish) {
			numberGrowthFish++;
		}
	}
	int result = 0;
	if ((numberGrowthFish >= singleVolumeFish) ||
		(numberGrowthFish == amountFish)) {
		result = numberGrowthFish;
	}
	return result;
}