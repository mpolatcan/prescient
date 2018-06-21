# Forecastbase

**Forecastbase** is a automated forecasting tool for businesses. Forecastbase
is based on **Facebook Prophet** API and configurable tool with several
parameters related with **Facebook Prophet** API.

## How it works

    python Forecastbase.py [config_filename.yml]

**Example**:

    python Forecastbase.py config.yml


## Forecastbase Config

```yaml
# Forecastbase Example Config
# Created by Mutlu Polatcan
# 01.02.2018

################################### REQUIRED ATTRIBUTES #####################################
forecastbase.dataset.filepath: "../datasets/energy-demand-forecasting/zone_1_energy_demand.csv"

forecastbase.training.data.percent.min: 70
forecastbase.training.data.percent.max: 80
forecastbase.training.data.percent.increment.by: 5

forecastbase.interval.width.min: 0.05
forecastbase.interval.width.max: 0.85
forecastbase.interval.width.increment.by: 0.05

forecastbase.changepoint.prior.scale.min: 0.001
forecastbase.changepoint.prior.scale.max: 0.5
forecastbase.changepoint.prior.scale.increment.by: 0.001

forecastbase.predict.next: 7
forecastbase.predict.freq: "D"

forecastbase.convergence.detection.acr.threshold: -0.5 # must be negative
forecastbase.convergence.detection.measure.number: 3

forecastbase.paralellism: 3

forecastbase.holiday.weekends.enabled: true

################################### OPTIONAL ATTRIBUTES #######################################
forecastbase.holiday.special.days:
  - "2017-01-30"
  - "2017-02-28"
```

### Config Attributes and Details
------------------------------------

#### *Training Data Percentage*
**Forecastbase** is automated forecasting tool and so that, it wants training data
percentage range from you. **Forecastbase** automatically creates training files according to
this percentage range and use these files for training models.

    NOTE !!! Valid values for this attribute is between 0 and 100

- **forecastbase.training.data.percent.min** (Type: *double*): Minimum percentage of training
data.
- **forecastbase.training.data.percent.max** (Type: *double*): Maximum percentage of training
data.
- **forecastbase.training.data.percent.increment.by** (Type: *double*): Incrementation amount of
percentage of training data.

------------------------------------

##### *Interval Width*
The biggest source of uncertainty in the forecast is the potential for future trend changes.
Again, these interval assume that the future will see the same frequency and magnitude of rate changes as the past.
we assume that **the future will see similar trend changes as the history**. In particular, we assume that the average frequency
and magnitude of trend changes in the future will be the same as that which we observe in the history. We project these trend
changes forward and by computing their distribution we obtain uncertainty intervals.
This assumption is probably not true, so you should not expect to get accurate coverage on these uncertainty intervals.
One property of this way of measuring uncertainty is that allowing **higher flexibility** in the rate, by increasing **forecastbase.changepoint.prior.scale**,
will increase the forecast uncertainty. This is because if we model more rate changes in the history then we will expect more in the future,
and makes the uncertainty intervals a useful indicator of **overfitting**.

- **forecastbase.interval.width.min** (Type: *double*): Minimum uncertainty interval width
- **forecastbase.interval.width.max** (Type: *double*): Maximum uncertainty interval width
- **forecastbase.interval.width.increment.by** (Type: *double*): Incrementation amount of uncertainty interval width

------------------------------------

##### *Changepoint Prior Scale*
**Facebook Prophet** API

- **forecastbase.changepoint.prior.scale.min:** (Type: *double*):
- **forecastbase.changepoint.prior.scale.max:** (Type: *double*):
- **forecastbase.changepoint.prior.scale.increment.by:** (Type: *double*):

------------------------------------

##### *Prediction Amount and Frequency*

- **forecastbase.predict.next** (Type: *integer*): How far do you want to see future ?
- **forecastbase.predict.freq** (Type: *string*): Prediction frequency for Forecastbase.

        NOTE !!! Valid frequencies are 'H', 'D', 'M', 'Y'

-----------------------------------

##### *Parallelism*
**Forecastbase** trains models and make predictions on these models concurrently. So that, there is attribute for
how many models train and make predictions on these models concurrently.

- **forecastbase.paralellism** (Type: *integer*): Parallelism amount of your CPU. If you
have a quad core CPU and assign **4** to this parameter in config file, **Forecastbase** trains
**4** models concurrently. If you increase this parameter, your total training and prediction time
will be reduced.

-----------------------------------

##### *Measure Number and Accuracy Change Rate Threshold for Convergence Detection*
**Forecastbase** is automated forecasting tool and so that it must be find best model for us. **Forecastbase**
uses simple optimization for this. **Forecastbase** looks last n (given by config) model's accuracies and compare
it with current best model. If average accuracy change rate, belows user defined threshold, **Forecastbase**
doesn't try any other parameters.

    NOTE !!! Average accuracy change rate threshold must be NEGATIVE

- **forecastbase.convergence.detection.acr.threshold** (Type: *double*): Threshold of average accuracy rate change.
- **forecastbase.convergence.detection.measure.number** (Type: *integer*): Model training and predictions numbers for
calculate average accuracy change rate by last n model's accuracies. (Window size)

-----------------------------------

##### *Special Days and Holidays*
**Forecastbase** also models holiday effects via **Facebook Prophet** API. **Forecastbase**
automatically finds weekends in time series data and gives it to the **Prophet** to train models
to modelling weekend effects. Also users can add special holidays for modelling holiday effects of these
days. For example, "Christmas", "Ramadan" etc.

- **forecastbase.holiday.weekends.enabled** (Type: *boolean*): Enable or disable **Forecastbase's**
    weekend effect modelling.
- **forecastbase.holiday.special.days** (Type: *list of date strings*): User defined special days for
holiday effect modelling.

-----------------------------------

