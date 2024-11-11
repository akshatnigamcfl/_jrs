from django import template
from console.models import UserAccount, Client, Booking
register = template.Library()

# @register.simple_tag()
def multiply(a, b, *args, **kwargs):
    # you would need to do any localization of the result here
    # print('qty*************8', a*b  )
    return a*b

register.filter('multiply',multiply)



def substract(a, b, *args, **kwargs):
    # you would need to do any localization of the result here
    # print('qty*************8', a*b  )
    return a-b


def add(a, b, *args, **kwargs):
    # you would need to do any localization of the result here
    # print('qty*************8', a*b  )
    return a+b


def loop_length_generator(a, *args, **kwargs):
    # you would need to do any localization of the result here
    # print('qty*************8', a*b  )
    data = ''
    for aa in range(a):
        data += str(0)
    return data


def includes(a,b, *args, **kwargs):
    # you would need to do any localization of the result here
    # print('qty*************8', a*b  )
    data = [ d.id for d in a]
    print('poolllllll',data)
    if b in data:
        return True
    else:
        return False


def customreplacespace(a, b, *args, **kwargs):
    return a.replace(b,' ')

def isadmin(id, *args, **kwargs):
    print(id)
    print('user account', UserAccount.objects.filter(user=id).exists())
    return UserAccount.objects.filter(user=id).exists()


# def stringToNumber(number, *args, **kwargs):
#     return int(number)


def clientObject(user_obj):
    if user_obj.id != None:
        client = Client.objects.filter(user = user_obj)
        if client.exists():
            return client.first()
    return None


def bookingTotalPriceObject(booking_obj):
    if booking_obj != None:

        total_price = 0
        additional_price = 0

        for b in booking_obj:
            for sd in b.shoot_date.all():
                for ads in sd.additional_service.all():
                    additional_price += ads.additional_service.price * ads.count

        total_price = (b.package.price - b.discount) + additional_price

        if total_price != 0:
            return total_price
    return None


def clientObjectWithReview(review_obj):
    if review_obj.id != None:
        client = Client.objects.filter(booking__review = review_obj)
        if client.exists():
            return client.first()
    return None


def clientObjectWithCustomModel(custom_model_obj):
    if custom_model_obj.id != None:
        client = Client.objects.filter(user = custom_model_obj)
        if client.exists():
            return client.first()
    return None


def bookingObjectWithReview(review_obj):
    if review_obj.id != None:
        booking = Booking.objects.filter(review = review_obj)
        if booking.exists():
            return booking.first()
    return None




register.filter('substract',substract)
register.filter('add',add)


register.filter('loop_length_generator',loop_length_generator)
register.filter('includes',includes)
register.filter('customreplacespace',customreplacespace)
register.filter('isadmin',isadmin)
# register.filter('stringToNumber',stringToNumber)
register.filter('clientObject',clientObject)
register.filter('bookingTotalPriceObject',bookingTotalPriceObject)
register.filter('clientObjectWithReview',clientObjectWithReview)
register.filter('clientObjectWithCustomModel',clientObjectWithCustomModel)
register.filter('bookingObjectWithReview',bookingObjectWithReview)
