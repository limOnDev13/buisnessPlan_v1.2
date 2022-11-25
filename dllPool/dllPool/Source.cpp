#include <stdio.h>
#include <math.h>


extern "C" __declspec(dllexport) bool has_there_been_enough_fish_sale(
	float* arrayMass,
	int amountFish,
	float massComercialFish,
	int singleVolumeFish,
	bool* result
)
{
	// количество выросших рыбок
	int numberGrowthFish = 0;
	for (int i = 0; i < amountFish; i++) {
		printf("%f ", arrayMass[i]);
		if (arrayMass[i] >= massComercialFish) {
			numberGrowthFish++;
			result[i] = true;
		}
	}
	printf("\n");

	if ((numberGrowthFish >= singleVolumeFish) ||
		(numberGrowthFish == amountFish)) {
		return true;
	}
	else return false;
}