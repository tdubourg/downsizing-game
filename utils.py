INFO = True
DBG = True
ERRORS = True
LOG = True

def init():
    # Syntax:
    # LOG_LEVEL = PREVIOUS_LOG_LEVEL | VALUE_FOR_THIS_LOG_LEVEL
    # Why this syntax? All "next" log levels will enabled as soon as you enabled a given log level
    # and if the previous log level is disabled, then we take the value for this log level...
    global DBG, ERRORS, LOG, INFO
    DBG = INFO | DBG
    ERRORS = DBG | ERRORS
    LOG = ERRORS | LOG
    
def log(*args):
    LOG_LEVEL = args[-1]
    if LOG_LEVEL:
        for s in args[0]:
            print s,
        print ""

def e(*args):
    log(args, ERRORS)

def l(*args):
    log(args, LOG)

def d(*args):
    log(args, DBG)

def i(*args):
    log(args, INFO)


init()  # This should indeed be run when the module is loaded, not and error

if __name__ == '__main__':
    LOG = False
    DBG = False
    ERRORS = False
    INFO = False
    init()
    print "Trying to output with every disabled..."
    e("Error")
    d("Debug")
    i("Info")
    l("Log")

    print "Trying LOG log level..."
    LOG = True
    init()
    e("Error")
    d("Debug")
    i("Info")
    l("Log")
    LOG = False

    print "Trying INFO log level..."
    INFO = True
    init()
    e("Error")
    d("Debug")
    i("Info")
    l("Log")
    INFO = False

    print "Trying DBG log level..."
    DBG = True
    init()
    e("Error", "hey", "ho")
    d("Debug")
    i("Info")
    l("Log")
    DBG = False

    print "Trying ERRORS log level..."
    ERRORS = True
    init()
    e("Error")
    d("Debug")
    i("Info")
    l("Log")
    ERRORS = False
