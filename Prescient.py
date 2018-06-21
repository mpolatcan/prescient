'''
Automated forecasting tool for businesses.

Developed by Mutlu Polatcan
01.02.2018
Version 0.1.0
'''

# TODO Get streaming data from Kafka
# TODO Online forecasting architecture
# TODO Model serialization
# TODO Time series database integration


import os
import subprocess
import numpy as np
import pandas as pd
import threading
import signal
from colorama import Fore
from concurrent.futures import ProcessPoolExecutor
from ProphetExecutor import ProphetExecutor
from PrescientConfig import PrescientConfig
from PrescientLogger import PrescientLogger
from collections import deque
import sys

# ------------------------ RESULT VARIABLES -----------------------
best_model = (0, 0, 0)
accuracies = deque()
accuracy_change_rates = deque()
best_accuracies = deque()
# -----------------------------------------------------------------

# ---------------------------------- CONFIGS ---------------------------------------
config = PrescientConfig(sys.argv[1])  # get configuration from file
dataset_filepath = config.get_str("forecastbase.dataset.filepath")
tdp_min = config.get_float("forecastbase.training.data.percent.min")
tdp_max = config.get_float("forecastbase.training.data.percent.max")
tdp_inc_by = config.get_float("forecastbase.training.data.percent.increment.by")
iw_min = config.get_float("forecastbase.interval.width.min")
iw_max = config.get_float("forecastbase.interval.width.max")
iw_inc_by = config.get_float("forecastbase.interval.width.increment.by")
cps_min = config.get_float("forecastbase.changepoint.prior.scale.min")
cps_max = config.get_float("forecastbase.changepoint.prior.scale.max")
cps_inc_by = config.get_float("forecastbase.changepoint.prior.scale.increment.by")
predict_next = config.get_int("forecastbase.predict.next")
predict_freq = config.get_str("forecastbase.predict.freq")
parallelism = config.get_int("forecastbase.paralellism")
measure_number = config.get_int("forecastbase.convergence.detection.measure.number")
average_acr_threshold = config.get_float("forecastbase.convergence.detection.acr.threshold")
holiday_weekends_enabled = config.get_bool("forecastbase.holiday.weekends.enabled")
holiday_special_days = config.get_list("forecastbase.holiday.special.days")
# -----------------------------------------------------------------------------------

# ----------------------------- HOLIDAY WEEKENDS SETTINGS -----------------------------
holiday_weekends = {}

if not holiday_weekends_enabled:
    holiday_weekends = None
# -------------------------------------------------------------------------------------

semaphore = threading.BoundedSemaphore(value=1)


def run():
    model_index = 1
    prophet_executor = ProphetExecutor()

    # Create training file and load weekends (if enabled) according to current percent
    for training_data_percent_prep in np.arange(tdp_min, tdp_max + tdp_inc_by, tdp_inc_by):
        prepare_training_file(training_data_percent_prep)

        if holiday_weekends_enabled:
            load_holiday_weekends(training_data_percent_prep)

    # Submitting jobs
    with ProcessPoolExecutor(max_workers=parallelism) as process_pool:
        for training_data_percent in np.arange(tdp_min, tdp_max + tdp_inc_by, tdp_inc_by):
            for interval_width in np.arange(iw_min, iw_max + iw_inc_by, iw_inc_by):
                for changepoint_prior_scale in np.arange(cps_min, cps_max + cps_inc_by, cps_inc_by):
                    model_future = process_pool.submit(prophet_executor.execute,
                                                       model_index,
                                                       dataset_filepath,
                                                       training_data_percent,
                                                       interval_width,
                                                       changepoint_prior_scale,
                                                       predict_next,
                                                       predict_freq,
                                                       holiday_weekends,
                                                       holiday_special_days)
                    model_future.add_done_callback(model_training_done_callback)
                    model_index += 1


def prepare_training_file(training_data_percent):
    # Get data count of file
    data_count = int(subprocess.Popen(["wc", "-l", dataset_filepath], stdout=subprocess.PIPE).communicate()[0].split()[0])

    # Calculate training data count according to percentage
    training_data_count = (data_count * training_data_percent) / 100

    PrescientLogger.console_log("FORECASTBASE", Fore.YELLOW, "Preparing training file for parameter training_data_percent=%" + str(training_data_percent) +
       " Original data count:" + str(data_count) + " Training data count: " + str(training_data_count))

    # Create training data file
    os.system("head -" + str(int(training_data_count)) + " " + dataset_filepath + " > " + os.path.basename(dataset_filepath).split('.')[0] +
            "_training_%" + str(training_data_percent) + ".csv")


def load_holiday_weekends(training_data_percent):
    global holiday_weekends

    PrescientLogger.console_log("FORECASTBASE", Fore.YELLOW, "Preparing weekends for parameter training_data_percent=%" + str(training_data_percent))

    df_training_data = pd.read_csv(os.path.basename(dataset_filepath).split('.')[0] + "_training_%" + str(training_data_percent) + ".csv")
    df_training_data['ds'] = pd.to_datetime(df_training_data['ds'])  # Convert string to datetime
    df_training_data['weekday'] = df_training_data['ds'].dt.weekday  # Find number of day
    df_training_data['ds'] = df_training_data['ds'].dt.date  # Truncate time from datetime

    # Selecting rows where day is Saturday or Sunday
    df_holiday_weekends = df_training_data[(df_training_data['weekday'] == 5) | (df_training_data['weekday'] == 6)]
    df_holiday_weekends = df_holiday_weekends.drop_duplicates(subset=['ds'])  # Drop duplicate rows
    df_holiday_weekends.drop(['y', 'weekday'], axis=1, inplace=True)  # Drop unnecessary columns

    holiday_weekends[str(training_data_percent)] = df_holiday_weekends


def show_intermediate_results(average_acr, acr_frame):
    PrescientLogger.console_log(
       None,
       Fore.BLUE,
       "########################################################################",
       "Last " + str(measure_number) + " model's accuracies and accuracy change rates: \n",
       acr_frame.to_string(),
       "\nAverage accuracy change rate: " + str(average_acr),
       "Best accuracy: " + str(best_model[0]),
       "########################################################################\n")


def model_training_done_callback(model_fn):
    global best_model

    semaphore.acquire()

    if model_fn.done():
        error = model_fn.exception()

        if error:
            print(error)
        else:
            model = model_fn.result()

            if accuracy_change_rates.__len__() < measure_number:
                accuracy_change_rates.append(model[0] - best_model[0])
                accuracies.append(model[0])
                best_accuracies.append(best_model[0])
            else:
                # Remove oldest data and add last data
                accuracy_change_rates.popleft()
                accuracies.popleft()
                best_accuracies.popleft()

                accuracy_change_rates.append(model[0] - best_model[0]); accuracies.append(model[0]); best_accuracies.append(best_model[0])

            # If trained model's accuracy is better than best model assign as new best model
            if model[0] > best_model[0]:
                best_model = model

            if accuracy_change_rates.__len__() == measure_number:
                # Calculate average accuracy change rate and show results
                acr_frame = pd.DataFrame({'best_accuracy': best_accuracies, 'last_model_accuracy': accuracies, 'acr': accuracy_change_rates})

                average_acr = acr_frame['acr'].mean()
                show_intermediate_results(average_acr, acr_frame)

                # If average accuracy change rate below threshold stop Forecastbase
                if average_acr < average_acr_threshold:
                    PrescientLogger.console_log("FORECASTBASE", Fore.RED, "Convergence Detected!! Best model is accuracy=" + str(best_model[0]) +
                          " training_data_percent=" + str(best_model[1]) + " interval_width=" + str(best_model[2]) + " changepoint_prior_scale=" + str(best_model[3]))

                    semaphore.release()  # Release acquired semaphore

                    # Remove training files
                    for training_data_percent in np.arange(tdp_min, tdp_max + tdp_inc_by, tdp_inc_by):
                        os.system("rm " + os.path.basename(dataset_filepath).split('.')[0] + "_training_%" + str(training_data_percent) + ".csv")

                    # Stop child processes and terminate program
                    child_pids = subprocess.Popen(["ps", "-o", "pid", "--ppid", str(os.getpid()), "--noheaders"],
                                                  stdout=subprocess.PIPE).communicate()[0].decode('ascii')
                    for child_pid in child_pids.split("\n")[:-1]:
                        try:
                            os.kill(int(child_pid), signal.SIGKILL)
                        except Exception:
                            continue

                    sys.exit()

    semaphore.release()


if __name__ == "__main__":
    run()
