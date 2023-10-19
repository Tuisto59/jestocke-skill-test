import json

from django.db.models import Value, CharField, F
from django.db.models.functions import Concat
from django.views.generic import ListView

from booking.models import Booking
from market_place.models import StorageBox


def serialize_storage_boxes(queryset):
    serialized_data = []
    for box in queryset:
        serialized_data.append({
            "id": box.id,
            "title": box.title,
            "description": box.description,
            "surface": box.surface,
            "monthly_price": {
                "amount": str(box.monthly_price.amount),
                "currency": str(box.monthly_price.currency)
            },

        })
    return json.dumps(serialized_data)


class AvailableStorageBoxesView(ListView):
    model = StorageBox
    template_name = 'market_place/available_boxes.html'
    context_object_name = 'available_boxes'
    paginate_by = 10  # Display 10 boxes per page. You can adjust this.

    def get_queryset(self):
        # Exclude boxes that are already booked
        booked_boxes = Booking.objects.values_list('storage_box', flat=True)
        qs = StorageBox.objects.exclude(id__in=booked_boxes)

        print("[DEBUUUUGGGG]", str(qs[0].monthly_price.__dict__))

        # Sorting
        dico_sort = {"price_asc": "price",  # since we don't have price
                     "price_desc": "-price",  # since we don't have price
                     "surface_asc": "surface",
                     "surface_desc": "-surface",
                     "address_asc": "full_address",
                     "address_desc": "-full_address"
                     }
        sort = self.request.GET.get('sort')
        if sort:
            if sort in ["address_asc", "address_desc"]:

                # Annotate with concatenated address field
                qs = qs.annotate(
                    full_address=Concat(
                        # can be more precise if needed :
                        # F('street_number'),
                        # Value(' '),
                        # F('route'),
                        # Value(' '),
                        # F('postal_code'),
                        Value(' '),
                        F('city'),
                        output_field=CharField()
                    )
                )

                # Sorting based on price
            elif sort in ["price_asc", "price_desc"]:
                qs = list(qs)
                prices = [{"amount": float(i.monthly_price.initial[0]), "currency": str(i.monthly_price.initial[1])} for
                          i in qs]
                indexed_qs = list(enumerate(qs))
                indexed_qs.sort(key=lambda ix: prices[ix[0]]['amount'], reverse=(sort == "price_desc"))
                qs = [item[1] for item in indexed_qs]

            else:
                qs = qs.order_by(dico_sort[sort])

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        prices = [{"amount": str(i.monthly_price.initial[0]), "currency": str(i.monthly_price.initial[1])} for i in qs]

        # Annotate each box with its corresponding price
        for box, price in zip(qs, prices):
            print(price)
            box.price = price

        context['available_boxes'] = qs
        print('in get_context_data', qs[0].__dict__)
        return context
