# use expriation dates Monthly SPX
# listSmartOptionChainSPX.expriations is a set
# change to sorted list
# =================================
# Problem with qalifyContract after Nov18
# API issue https://groups.io/g/insync/topic/7790846?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,7790846
# shorten the expiry timeline for now.. 3/23/18
sortedExpiry = sorted(listSmartOptionChainSPX.expirations)
# Month iWidget
aMonth =  widgets.SelectionSlider(
# Shorten the expiry to 4
        options = sortedExpiry[:4],
        description='SPX Thurs:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True
)
# year iWidget
aYear = widgets.RadioButtons(
    options=['2018', '2019'],
    value='2018',
    description='Year:',
    disabled=False
)
# price iWidget
aStrikePriceRange = widgets.IntSlider(
    value=20,
    min=5,
    max=50,
    step=5,
    description='$Range:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)
# price iWidget
aStrikePriceMultiple = widgets.IntSlider(
    value=5,
    min=1,
    max=10,
    step=1,
    description='$Multiple:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)
# price iWidget
aStrikePriceMultiple = widgets.IntSlider(
    value=5,
    min=1,
    max=10,
    step=1,
    description='$Multiple:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)
# ne# price iWidget
numberOfContracts = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    description='# of Contracts:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)
