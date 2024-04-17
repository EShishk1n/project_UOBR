from datetime import date

from django.test import TestCase

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition, NextPosition
from dvizhenie.services.give_statuses_to_pads.common_function import give_status_to_pads
from dvizhenie.services.give_statuses_to_pads.give_status_drilled_to_pads import get_drilled_pads, \
    give_status_drilled_to_pads, get_dislocated_rigs_list, get_all_rigs_id_list
from dvizhenie.services.give_statuses_to_pads.give_status_drilling_to_pads import \
    give_status_drilling_to_pads, convert_from_QuerySet_to_list, get_drilling_pads_id
from dvizhenie.services.give_statuses_to_pads.give_status_free_to_pads import give_status_free_to_pads, get_free_pads_id
from dvizhenie.services.give_statuses_to_pads.give_status_reserved_to_pads import \
    give_status_reserved_to_pads, get_reserved_pads_id
from dvizhenie.services.give_statuses_to_pads.give_statuses_to_pads import give_statuses_to_pads


class CommonFunctionTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')

    def test_give_status_to_pads(self):

        self.assertEquals(Pad.objects.get(number=133).status, '')
        give_status_to_pads([Pad.objects.get(number=133).id], 'drilling')
        self.assertEquals(Pad.objects.get(number=133).status, 'drilling')

    def test_convert_from_QuerySet_to_list(self):
        queryset = Pad.objects.all().values_list('id')
        list_from_Queryset = convert_from_QuerySet_to_list(queryset)
        self.assertEquals(list_from_Queryset, [Pad.objects.get(number=133).id, Pad.objects.get(number=110).id])


class GiveStatusDrilledToPadsTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')

        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_2,
                                                         start_date=date(2024, 5, 1), end_date=date(2024, 10, 1))

    def test_get_all_rigs_list(self):
        all_rigs_list = get_all_rigs_id_list()
        self.assertEquals(all_rigs_list, {DrillingRig.objects.get(number=666).id: 2})

    def test_get_dislocated_rigs_list(self):
        dislocated_rigs_list = get_dislocated_rigs_list()
        self.assertEquals(dislocated_rigs_list, [DrillingRig.objects.get(number=666).id])

    def test_get_drilled_pads(self):
        drilled_pads = get_drilled_pads()
        self.assertEquals(drilled_pads, [Pad.objects.get(number=133).id])

    def test_give_status_drilled_to_pads(self):
        self.assertEquals(Pad.objects.get(number=133).status, '')
        give_status_drilled_to_pads()
        self.assertEquals(Pad.objects.get(number=133).status, 'drilled')


class GiveStatusDrillingToPadsTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='drilled')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')

        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_2,
                                                         start_date=date(2024, 5, 1), end_date=date(2024, 10, 1))

    def test_get_drilling_pads(self):
        drilling_pads = get_drilling_pads_id()
        self.assertEquals(drilling_pads[0][0], Pad.objects.get(number=110).id)

    def test_give_status_drilling_to_pads(self):
        self.assertEquals(Pad.objects.get(number=110).status, '')
        give_status_drilling_to_pads()
        self.assertEquals(Pad.objects.get(number=110).status, 'drilling')


class GiveStatusReservedToPadsTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='drilled')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.next_position_1 = NextPosition.objects.create(current_position=self.rig_position_1,
                                                           next_position=self.pad_2, status='changed')

    def test_get_reserved_pads(self):
        reserved_pads = get_reserved_pads_id()
        self.assertEquals(reserved_pads[0][0], Pad.objects.get(number=110).id)

    def test_give_status_reserved_to_pads(self):
        self.assertEquals(Pad.objects.get(number=110).status, '')
        give_status_reserved_to_pads()
        self.assertEquals(Pad.objects.get(number=110).status, 'reserved')


class GiveStatusFreeToPadsTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='drilled')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')
        self.pad_3 = Pad.objects.create(number='58', field='СУГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=6,
                                        nns_quantity=8, status='drilling')
        self.pad_4 = Pad.objects.create(number='637у', field='МБ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=250, required_mud='РВО', gs_quantity=0,
                                        nns_quantity=24, status='')

    def test_get_free_pads(self):
        free_pads = get_free_pads_id()
        self.assertEquals(free_pads[0][0], Pad.objects.get(number=110).id)
        self.assertEquals(len(free_pads), 2)

    def test_give_status_free_to_pads(self):
        self.assertEquals(Pad.objects.get(number=110).status, '')
        self.assertEquals(Pad.objects.get(number='637у').status, '')
        give_status_free_to_pads()
        self.assertEquals(Pad.objects.get(number=110).status, 'free')
        self.assertEquals(Pad.objects.get(number='637у').status, 'free')


class GiveStatusesToPadsTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')
        self.pad_3 = Pad.objects.create(number='58', field='СУГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=6,
                                        nns_quantity=8, status='')
        self.pad_4 = Pad.objects.create(number='637у', field='МБ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=250, required_mud='РВО', gs_quantity=0,
                                        nns_quantity=24, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_2,
                                                         start_date=date(2024, 5, 1), end_date=date(2024, 10, 1))
        self.next_position_1 = NextPosition.objects.create(current_position=self.rig_position_2,
                                                           next_position=self.pad_3, status='changed')

    def test_give_statuses_to_pads(self):

        self.assertEquals(Pad.objects.get(number=133).status, '')
        self.assertEquals(Pad.objects.get(number=110).status, '')
        self.assertEquals(Pad.objects.get(number=58).status, '')
        self.assertEquals(Pad.objects.get(number='637у').status, '')

        give_statuses_to_pads()

        self.assertEquals(Pad.objects.get(number=133).status, 'drilled')
        self.assertEquals(Pad.objects.get(number=110).status, 'drilling')
        self.assertEquals(Pad.objects.get(number=58).status, 'reserved')
        self.assertEquals(Pad.objects.get(number='637у').status, 'free')
