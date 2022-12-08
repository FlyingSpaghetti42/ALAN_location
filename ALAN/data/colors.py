
def colors(subclass_check):
    if len(subclass_check) == 1:
        color = {
                subclass_check[0] : 'blue',
                }
    elif len(subclass_check) == 2:
        color = {
                subclass_check[0] : 'blue',
                subclass_check[1] : 'green'
                }
    elif len(subclass_check) == 3:
        color = {
                subclass_check[0] : 'blue',
                subclass_check[1] : 'green',
                subclass_check[2] : 'pink'
                }
    elif len(subclass_check) == 4:
        color = {
                subclass_check[0] : 'blue',
                subclass_check[1] : 'green',
                subclass_check[2] : 'pink',
                subclass_check[3] : 'red'
                }
    elif len(subclass_check) == 5:
        color = {
                subclass_check[0] : 'blue',
                subclass_check[1] : 'green',
                subclass_check[2] : 'pink',
                subclass_check[3] : 'lightgreen',
                subclass_check[4] : 'red'
                }
    return color
