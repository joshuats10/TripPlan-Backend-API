from django.conf import settings
from django.utils.timezone import make_aware

from pyqubo import Array, Constraint, Placeholder
from datetime import datetime, timedelta, date
from openjij import SQASampler
import numpy as np
import requests
import random


class CreateTripPlan:
    def __init__(self, date, start_time, end_time, places):
        self.date = make_aware(datetime.strptime(date, '%Y-%m-%d'))
        self.year = self.date.year
        self.month = self.date.month
        self.day = self.date.day
        self.travel_start = make_aware(datetime.combine(self.date, datetime.strptime(start_time, '%H:%M').time()))
        self.travel_end = make_aware(datetime.combine(self.date, datetime.strptime(end_time, '%H:%M').time()))
        
        self.places = places
        self.places_name = [places[i]['place_name'] for i in range(len(self.places))]
        self.places_name_idx = {name: idx for idx, name in enumerate(self.places_name)}
        self.places_id = [places[i]['place_id'] for i in range(len(self.places))]

        # Setting up priority
        p_min = 1
        p_max = len(self.places_name)
        self.priority = np.array([random.randint(p_min, p_max) for _ in range(len(self.places_name))])

        # Setting up staying time
        s_min = 15
        s_max = 75
        self.staying_times = [random.randint(s_min, s_max) for _ in range(len(self.places_name))]

    def get_opening_closing_times(self):
        trip_date = date(self.year, self.month, self.day)
        self.open_close = []
        for id in self.places_id:
            place_api_url = 'https://maps.googleapis.com/maps/api/place/details/json?'
            params = {
                'key': settings.MAPS_API_KEY,
                'place_id': id
            }

            response = requests.get(place_api_url, params=params)
            open_periods = response.json()['result']['current_opening_hours']['periods']

            for period in open_periods:
                if period['open'].get('truncated'):
                    self.open_close.append(['0000','2359'])
                    break
                elif period['open']['day'] == trip_date.weekday():
                    self.open_close.append([period['open']['time'], period['close']['time']])

    def get_duration_values(self):
        distance_matrix_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
        place_id_matrix = [f'place_id:{id}' for id in self.places_id]
        destinations = "|".join(place_id_matrix)
        params = {
            'key': settings.MAPS_API_KEY,
            'destinations': destinations,
            'origins': destinations
        }

        response = requests.get(distance_matrix_url, params=params)
        rows = response.json()['rows']
        self.duration_values = [[element['duration']['value'] for element in row['elements']] for row in rows]

    def trip_planning(self):

        def get_h_m_s(sec):
            td = timedelta(seconds=sec)
            m, s = divmod(td.seconds, 60)
            h, m = divmod(m, 60)
            return h, m, s

        def get_h_m_from_hhmm(hhmm):
            h = hhmm // 100
            m = hhmm % 100
            return h, m


        def get_h_m_from_mm(mm):
            h = mm // 60
            m = mm % 60
            return h, m

        # open_closeをdatetimeに変換する関数
        def make_datetime_business_hours(year, month, day, open_close):
            business_hours = []
            for i in range(len(open_close)):
                open_time = get_h_m_from_hhmm(int(open_close[i][0]))
                close_time = get_h_m_from_hhmm(int(open_close[i][1]))

                open_date = make_aware(datetime(year, month, day, open_time[0], open_time[1]))
                close_date = make_aware(datetime(year, month, day, close_time[0], close_time[1]))
                business_hours.append([open_date, close_date])
            return business_hours

        def make_timedelta_Time_t(duration_values):
            var = len(duration_values)
            row = len(duration_values[0])
            Time_t =[[0] * row for i in range(var)]
            for i in range(var):
                for j in range(row):
                    t = get_h_m_s(duration_values[i][j])
                    Time_t[i][j] = timedelta(hours = t[0], minutes = t[1],  seconds = t[2])
            return Time_t

        def make_timedelta_Time_s(staying_times):
            row = len(staying_times)
            Time_s = [0] * row
            for i in range(row):
                t = get_h_m_from_mm(staying_times[i])
                Time_s[i] = timedelta(hours = t[0], minutes = t[1])
            return Time_s

        # エネルギーの最小値を見つける関数
        def find_min_energy(samp):
            energies = []
            for i in range(len(samp)):
                energies.append(samp[i][1])
            return min(energies)

        # 最適解を見つける関数
        # エネルギーの最小値を利用する : (A)
        def find_optimal_solutions(samp, ene):
            optimal_solutions = []
            for i in range(len(samp)):
                if samp[i][1] == ene: # (A)
                    optimal_solutions.append(samp[i][0])
            return optimal_solutions

        # 営業時間外に出入りするポイントの数を報告
        def find_min_violation(optimal_solutions, n):
            cnt_violations = []
            for i in range(len(optimal_solutions)):
                cnt_violations.append(check_business_hours(optimal_solutions[i], n))
            return min(cnt_violations)

        def find_exact_solutions(optimal_solutions, min_vlt, n):
            exact_solutions = []
            for i in range(len(optimal_solutions)):
                if check_business_hours(optimal_solutions[i], n) == min_vlt:
                    exact_solutions.append([optimal_solutions[i], check_business_hours(optimal_solutions[i], n)])
            return exact_solutions

        # 解の行列を訪問順に分ける関数
        def split_array(result, div):
            result_split = []
            for i in range(div):
                if any(np.array_split(result, div)[i]) == True: 
                    result_split.append(np.array_split(result, div)[i])        
            return result_split

        def check_business_hours(visiting_list, div):
            splited_visiting_list = split_array(visiting_list, div)
            organized_n = len(splited_visiting_list)
            cnt_violation = 0
            enter_time = self.travel_start
            exit_time = self.travel_start
            for i in range(organized_n):
                if i == 0:
                    continue
                else:
                    enter_time = exit_time + Time_t[int(np.where(splited_visiting_list[i-1]==1)[0])][int(np.where(splited_visiting_list[i]==1)[0])]
                    exit_time = enter_time + Time_s[int(np.where(splited_visiting_list[i]==1)[0])]
                
                ## スタートとゴール出入場時間を考えるかどうか　##

                if i == 0:
                    continue
                if i == organized_n - 1:
                    if not(business_hours[int(np.where(splited_visiting_list[i])[0])][0] <= enter_time and enter_time <= business_hours[int(np.where(splited_visiting_list[i])[0])][1]):
                        cnt_violation += 1
                else:

                    if not(business_hours[int(np.where(splited_visiting_list[i])[0])][0] <= enter_time and enter_time <= business_hours[int(np.where(splited_visiting_list[i])[0])][1]):
                        cnt_violation += 1
                    if not(business_hours[int(np.where(splited_visiting_list[i])[0])][0] <= exit_time and exit_time <= business_hours[int(np.where(splited_visiting_list[i])[0])][1]):
                        cnt_violation += 1
            return cnt_violation

        def make_timetable(sol, n):
            array = split_array(sol, n)
            organized_n = len(array)
            enter_time = self.travel_start
            exit_time = self.travel_start

            sol_transit_times = []
            sol_staying_times = []

            sol_enter_times = []
            sol_exit_times = []

            for i in range(organized_n):

                if i == 0:
                    enter_time = self.travel_start
                    exit_time = self.travel_start
                else:
                    enter_time = exit_time + Time_t[int(np.where(array[i-1]==1)[0])][int(np.where(array[i]==1)[0])]
                    exit_time = enter_time + Time_s[int(np.where(array[i]==1)[0])]

                # 移動時間
                if i != 0:
                    sol_transit_times.append(Time_t[int(np.where(array[i-1]==1)[0])][int(np.where(array[i]==1)[0])])

                # 滞在時間
                sol_staying_times.append(Time_s[int(np.where(array[i]==1)[0])])

                # 入場時間
                if i == 0:
                    sol_enter_times.append('NaN')
                else:
                    sol_enter_times.append(enter_time)

                # 退場時間
                if i == organized_n - 1:
                    sol_exit_times.append('NaN')
                else:
                    sol_exit_times.append(exit_time)
            
            return sol_transit_times, sol_staying_times, sol_enter_times, sol_exit_times
        
        def sol_timetable(exact_solutions ,n):

            timetable_travel = []
            timetable_stay = []
            timetable_enter = []
            timetable_exit = []

            for i in range(len(exact_solutions)):
                timetable_travel.append(make_timetable(exact_solutions[i], n)[0])
                timetable_stay.append(make_timetable(exact_solutions[i], n)[1])
                timetable_enter.append(make_timetable(exact_solutions[i], n)[2])
                timetable_exit.append(make_timetable(exact_solutions[i], n)[3])
            
            return timetable_travel, timetable_stay, timetable_enter, timetable_exit

        def make_order_of_visits(exact_solutions, n):
            order_of_visits = []

            for j in range(len(exact_solutions)):
                tmp = []
                sol = exact_solutions[j]
                splited_sol = split_array(sol, n)
                for i in range(len(splited_sol)):
                    tmp.append(int(np.where(splited_sol[i]==1)[0]))
                order_of_visits.append(tmp)
            
            return order_of_visits

        def make_uniq_exact_sol(exact_solutions):
            tmp = []
            for i in range(len(exact_solutions)):
                tmp.append(exact_solutions[i][0])
            arr = tmp
            uniq_arr = np.unique(arr, axis=0)

            return uniq_arr

        def make_route(sol, n, place_names):
            splited_sol = split_array(sol, n)
            order = []
            for i in range(len(splited_sol)):
                order.append(place_names[int(np.where(splited_sol[i]==1)[0])])
            return order

        def make_routes(sols, n, place_names):
            orders = []
            for i in range(len(sols)):
                orders.append(make_route(sols[i], n, place_names))
            return orders

        schedule_time = self.travel_end - self.travel_start
        travel_time = get_h_m_s(schedule_time.seconds)[0] * 60 + get_h_m_s(schedule_time.seconds)[1]
        business_hours = make_datetime_business_hours(self.year, self.month, self.day, self.open_close)
        transit_times = np.array(self.duration_values) // 60

        Time_t = make_timedelta_Time_t(self.duration_values)
        Time_s = make_timedelta_Time_s(self.staying_times)
        
        Max_time = max(max(transit_times.flatten()), max(self.staying_times))
        MMN_transit_times = transit_times / Max_time
        MMN_staying_times = np.array(self.staying_times) / Max_time
        MMN_travel_time = travel_time / Max_time
        MMN_Priority = self.priority / max(self.priority)

        N = len(self.places_name)

        # priority
        s = MMN_Priority
        # staying time
        c = MMN_staying_times
        # transit time
        d = MMN_transit_times
        # max number of visiting destination
        n = N
        # choice of destination
        m = N
        # enter start and goal
        vs = 0
        ve = 1
        # binary行列の作成
        x = Array.create('x', (n, m), 'BINARY')

        H_cost = Constraint(-sum(sum(s[v]*x[u,v] for u in range(n)) for v in range(m)), 'omega')
        H_a = Constraint(sum( (0.5 - sum(x[u,v] for v in range(m))) ** 2 for u in range(n)), 'alpha')
        B1 = sum(sum(c[v]*x[u, v] for u in range(n)) for v in range(m))
        B2 = sum(sum(sum(d[i][j]*x[u,i]*x[u+1,j] for j in range(m)) for i in range(m)) for u in range(n-1))
        H_b = Constraint((B1 + B2 - MMN_travel_time), 'beta')
        H_c = Constraint(sum( (0.5 - sum(x[u,v] for u in range(n) )) ** 2 for v in range(m)), 'gamma')
        H_d = Constraint(2 - x[0,vs] - x[n-1, ve], 'delta')

        param = (n*(0.5-m)**2 + sum(c)+sum(sum(d)) + m*(0.5-n)**2) / 3

        # ハミルトニアン
        H =  Placeholder('omega')*H_cost + Placeholder('alpha')*H_a + Placeholder('beta')*H_b + Placeholder('gamma')*H_c + Placeholder('delta')*H_d

        # hyper parameter
        params = {
            'omega': travel_time,
            'alpha': (1 + param/(n*(0.5-m)**2)) * travel_time,
            'beta': 1,
            'gamma': (1 + param/(m*(0.5-n)**2)) * travel_time,
            'delta': (1 + param/sum(s) * travel_time)
        }

        model = H.compile()
        qubo, offset = model.to_qubo(feed_dict=params)
        sampler = SQASampler()

        num_reads=50 * N 
        sampleset = sampler.sample_qubo(qubo,num_reads=num_reads)

        min_energy = find_min_energy(sampleset.record)
        optimal_solutions = find_optimal_solutions(sampleset.record, min_energy)

        min_vlt = find_min_violation(optimal_solutions, n)
        exact_solutions = find_exact_solutions(optimal_solutions, min_vlt, n)
        uniq_exact_sols = make_uniq_exact_sol(exact_solutions)

        timetable = sol_timetable(uniq_exact_sols, n)
        order_of_visits = make_order_of_visits(uniq_exact_sols, n)
            
        routes = make_routes(uniq_exact_sols, n, self.places_name)

        # exact_solutions[0] = [ [ (sol) ], cnt_vlt ]
        return uniq_exact_sols, order_of_visits, timetable, routes

    def get_optimal_trip_plan(self):
        self.get_opening_closing_times()
        self.get_duration_values()

        _, order, timetables, routes = self.trip_planning()

        for idx, i in enumerate(order[0]):
            self.places[i]['travel_order'] = idx + 1
            
            self.places[i]['stay_time'] = timetables[1][0][idx]

            if idx == 0:
                self.places[i]['arrival_time'] = None
            else:
                self.places[i]['arrival_time'] = timetables[2][0][idx]

            if idx == len(order[0]) - 1:
                self.places[i]['next_destination_travel_time'] = None
                self.places[i]['departure_time'] = None
            else:
                self.places[i]['next_destination_travel_time'] = timetables[0][0][idx]
                self.places[i]['departure_time'] = timetables[3][0][idx]
            
            self.places[i]['next_destination_mode'] = 'car'

        return self.places
