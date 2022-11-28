extern "C" __declspec(dllexport) float update_biomass(float*, int);
extern "C" __declspec(dllexport) float daily_work(float*, float*, int, float, float*);
extern "C" __declspec(dllexport) float do_daily_work_some_days(float*, float*, int, float, float*, int);
extern "C" __declspec(dllexport) int calculate_when_fish_will_be_sold(float*, float*, int, float, float*, float, int);
extern "C" __declspec(dllexport) int calculate_when_density_reaches_limit(float*, float*, int, float, float*, float, float);
extern "C" __declspec(dllexport) int calculate_how_many_fish_needs(float*, float*, float*, int, float, float*,
																   float*, float, int, float, float, int*);
extern "C" __declspec(dllexport) float calculate_density_after_some_days(float*, float*, int, float, float*, int, float);