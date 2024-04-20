from datetime import date

from django.test import TestCase

from dvizhenie.models import NextPosition, RigPosition, DrillingRig, Contractor, type_of_DR, Pad, PositionRating
from dvizhenie.services.funcs_for_views.change_next_position import put_new_next_position_in_NextPosition, \
    delete_next_position_if_alredy_in_model, give_status_free_to_pad_in_previous_NextPosition, change_next_position


class ChangeNextPositionTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='drilling')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')
        self.pad_3 = Pad.objects.create(number='669', field='МБ',
                                        first_stage_date=date(2024, 2, 26),
                                        second_stage_date=date(2024, 3, 16),
                                        required_capacity=320, required_mud='РУО', gs_quantity=14,
                                        nns_quantity=4, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.next_position = NextPosition.objects.create(current_position=self.rig_position_1, next_position=self.pad_2,
                                                         status='')
        self.position_rating = PositionRating.objects.create(current_position=self.rig_position_1,
                                                             next_position=self.pad_3,
                                                             capacity_rating=6,
                                                             first_stage_date_rating=5,
                                                             second_stage_date_rating=5,
                                                             mud_rating=6,
                                                             logistic_rating=4,
                                                             marker_rating=7,
                                                             common_rating=55,
                                                             status='')

    def test_put_new_next_position_in_NextPosition(self):
        put_new_next_position_in_NextPosition(self.rig_position_1, self.pad_3)

        self.assertEquals(NextPosition.objects.all()[0].next_position, self.pad_3)
        self.assertEquals(NextPosition.objects.all()[0].status, 'changed')

    def test_delete_next_position_if_alredy_in_model(self):
        delete_next_position_if_alredy_in_model(self.pad_2)
        self.assertEquals(NextPosition.objects.all()[0].next_position, None)

    def test_give_status_free_to_pad_in_previous_NextPosition(self):
        give_status_free_to_pad_in_previous_NextPosition(self.rig_position_1)

        self.assertEquals(Pad.objects.get(number='110').status, 'free')

    def test_change_next_position(self):
        change_next_position(self.position_rating)

        self.assertEquals(Pad.objects.get(number='110').status, 'free')
        self.assertEquals(NextPosition.objects.all()[0].next_position, self.pad_3)
        self.assertEquals(NextPosition.objects.all()[0].status, 'changed')
