import logging

logging.basicConfig(
                    level=logging.INFO,
                    # format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', #返回值：Thu, 26 May 2016 15:09:31 t11.py[line:92] INFO
                    format='%(asctime)s %(levelname)s %(message)s',
                    # datefmt='%a, %d %b %Y %H:%M:%S',
                    # datefmt='%Y/%m/%d %I:%M:%S %p', #返回2016/05/26 03:12:56 PM
                    datefmt='%Y-%m-%d %H:%M:%S',  # 返回2016/05/26 03:12:56 PM
                    # filename='./refresh.log'
                    )


def get_logger(name):
    return logging.getLogger(name)
