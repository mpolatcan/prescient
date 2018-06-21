# Created by Mutlu Polatcan
# 01.02.2018

import os
import time
from fbprophet import Prophet
import pandas as pd
import numpy as np
from colorama import Fore
from ProphetOutputSuppressor import ProphetOutputSuppressor
from ForecastbaseLogger import ForecastbaseLogger


class ProphetExecutor:
    def __init__(self):
        pass

    def execute(self, model_index, file_path, training_data_percent, interval_width, changepoint_prior_scale, predict_next, predict_freq,
                holiday_weekends, holiday_special_days):
        log_owner = "MODEL - " + str(model_index)

        start_time = time.time()

        # ---------------------------------------------- TRAINING PHASE ------------------------------------------------
        ForecastbaseLogger.console_log(log_owner, Fore.CYAN, "Training model with parameters training_data_percent=" + str(training_data_percent) +
           " interval_width=" + str(interval_width) + " changepoint_prior_scale=" + str(changepoint_prior_scale))

        # Read training and original data
        df_training_data = pd.read_csv(os.path.basename(file_path).split('.')[0] + "_training_%" + str(training_data_percent) + ".csv")
        df_original_data = pd.read_csv(file_path)
        
        df_training_data['y'] = np.log(df_training_data['y'])

        prophet_holiday_weekends = None
        prophet_holiday_special_days = None

        if holiday_weekends is not None:
            prophet_holiday_weekends = pd.DataFrame({
                                             'holiday': 'weekends',
                                             'ds': holiday_weekends[str(training_data_percent)].ds,
                                             'lower_window': 0,
                                             'upper_window': 1})

        if holiday_special_days is not None:
            prophet_holiday_special_days = pd.DataFrame({
                                             'holiday': 'special_days',
                                             'ds': pd.to_datetime(holiday_special_days),
                                             'lower_window': 0,
                                             'upper_window': 1})

        if (holiday_weekends is not None) and (holiday_special_days is not None):
            # Union weekends and user defined special days
            prophet_holidays = pd.concat(prophet_holiday_weekends,prophet_holiday_special_days)
            prophet = Prophet(holidays=prophet_holidays, interval_width=interval_width, changepoint_prior_scale=changepoint_prior_scale)
        elif holiday_weekends is not None:
            prophet = Prophet(holidays=prophet_holiday_weekends, interval_width=interval_width, changepoint_prior_scale=changepoint_prior_scale)
        elif holiday_special_days is not None:
            prophet = Prophet(holidays=prophet_holiday_special_days, interval_width=interval_width, changepoint_prior_scale=changepoint_prior_scale)
        else:
            prophet = Prophet(interval_width=interval_width, changepoint_prior_scale=changepoint_prior_scale)

        # Train model and predict future
        with ProphetOutputSuppressor():
            model = prophet.fit(df_training_data)
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------- PREDICTION PHASE -----------------------------------------------
        ForecastbaseLogger.console_log(log_owner, Fore.GREEN, "Predicting next " + str(predict_next) + " " + self.__get_predict_freq_str(predict_freq))

        df_future = model.make_future_dataframe(periods=predict_next, freq=predict_freq)
        df_forecast_result = model.predict(df_future)
        # --------------------------------------------------------------------------------------------------------------

        # ----------------------------------------- ACCURACY CALCULATION PHASE -----------------------------------------
        # Convert data to corresponding values
        df_forecast_result['yhat'] = np.exp(df_forecast_result['yhat'])

        # Get future predictions
        df_future_predictions = df_forecast_result.tail(predict_next)

        df_testing_accuracy = df_future_predictions.set_index('ds')[['yhat']].join(df_original_data.set_index('ds').y).reset_index()
        df_testing_accuracy.dropna(inplace=True)  # Remove NaN results
            
        # Calculate mean absolute percentage error
        df_testing_accuracy['percentage'] = abs(df_testing_accuracy['yhat'] - df_testing_accuracy['y']) / df_testing_accuracy['y']
        testing_error = (df_testing_accuracy['percentage'].sum() / len(df_testing_accuracy.index)) * 100
        testing_accuracy = 100 - testing_error

        ForecastbaseLogger.console_log(log_owner, Fore.YELLOW, "Result: Accuracy: " + str(testing_accuracy) + " interval_width: " + str(interval_width) +
                " changepoint_prior_scale: " + str(changepoint_prior_scale))

        end_time = time.time()

        ForecastbaseLogger.console_log(log_owner, Fore.RED, "Elapsed time: " + time.strftime("%H:%M:%S", time.gmtime(end_time - start_time)))
        # --------------------------------------------------------------------------------------------------------------

        return testing_accuracy, training_data_percent, interval_width, changepoint_prior_scale

    def __get_predict_freq_str(self, predict_freq):
        if predict_freq == "D":
            return "days"
        elif predict_freq == "M":
            return "months"
        elif predict_freq == "H":
            return "hours"
