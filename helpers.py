import datetime
import os
import telebot


# write text to html file
def write_to_html(filename, text):
    f = open(filename, 'w')
    f.write('<meta charset="UTF-8">')
    f.write(text)
    f.close()


# write messages to logs
def write_to_log(message, send_to_montitor_channel=True):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # set correct timezone
    cst_time_delta = datetime.timedelta(hours=2)
    tzObject = datetime.timezone(cst_time_delta, name="IST")

    filename = datetime.datetime.today().strftime("%d-%m-%Y")
    time = datetime.datetime.now(tzObject).strftime("%H:%M:%S")

    f = open('logs/' + filename + '.log', 'a')
    f.write('=============================================' + time + '=============================================\n')
    f.write(message + '\n')
    f.write('==================================================================================================\n\n\n')
    f.close()
    if send_to_montitor_channel:
        telebot.send_to_monitoring_channel(message)
    exit()
