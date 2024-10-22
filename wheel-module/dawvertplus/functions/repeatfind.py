# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dawvertplus.functions import xtramath
#from dawvertplus.functions import data_values
from dawvertplus.functions import data_regions

# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- Find Loop --------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------

cond_values_tres = 0.05
cond_same_loc_tres = 0.5
cond_null_tres = 0.4

def subfind(lst_numberlist_in, foundlocs, patnum):
	foundlocs_cur = [x for x in foundlocs]
	highestloc = max(foundlocs)
	numlistlen = len(lst_numberlist_in)
	lst_numberlist = lst_numberlist_in.copy()
	lst_numberlist += [None for _ in range(numlistlen)]

	out_length = 0
	#print(patnum, foundlocs)

	while highestloc < numlistlen:
		foundlocs_cur = [x+1 for x in foundlocs_cur]

		precond_values = [lst_numberlist[x] for x in foundlocs_cur]
		cond_values = 1 - xtramath.average([int(x == precond_values[0]) for x in precond_values])
		cond_null = 1 - xtramath.average([int(x == None) for x in precond_values])

		precond_same_loc = [int(x in foundlocs) for x in foundlocs_cur]
		cond_same_loc = xtramath.average(precond_same_loc)

		bool_values = cond_values > cond_values_tres
		bool_same_loc = cond_same_loc > cond_same_loc_tres
		bool_cond_null = cond_null < cond_null_tres

		#print('---', out_length, '|', precond_values, cond_values, bool_values, '|', precond_same_loc, cond_same_loc, bool_same_loc)
		if bool_same_loc or bool_values or bool_cond_null: break
		else:
			highestloc += 1
			out_length += 1

	regions = [[x, out_length] for x in foundlocs]
	if out_length > 1:
		return regions
	else:
		return []

def find(in_numberlist, in_reversed):
	#print('---------------- repeat find ----------------')

	lst_numberlist = in_numberlist.copy()

	len_numberlist = len(in_numberlist)

	#print(lst_numberlist)

	if in_reversed == True: lst_numberlist = lst_numberlist[::-1]

	lst_existing = []
	for x in lst_numberlist:
		if x != None: lst_existing.append(x)

	len_numberlist = len(lst_numberlist)

	numbdone = []

	regionsdata = []

	for patnum in lst_existing:
		foundlocs = [ind for ind, ele in enumerate(lst_numberlist) if ele == patnum]
		if patnum not in numbdone:
			if len(foundlocs) > 1:
				regions = subfind(lst_numberlist, foundlocs, patnum)

				if in_reversed == True: regions = data_regions.reverse(regions, len_numberlist)

				if regions != []:
					regionsdata.append([patnum, regions])
			numbdone.append(patnum)

	used_areas = [False for _ in range(len_numberlist) ]
	d_endpoints = {}
	for s_regionsdata in regionsdata:
		for s_reg in s_regionsdata[1]:
			endpointval = s_reg[0]+s_reg[1]

			for num in range(s_reg[0], s_reg[0]+s_reg[1]):
				used_areas[num] = True

			if endpointval not in d_endpoints: d_endpoints[endpointval] = 0
			d_endpoints[endpointval] += 1

	for d_endpoint in d_endpoints:
		if len(regionsdata) > 4:
			if d_endpoints[d_endpoint] > 1: used_areas[d_endpoint] = False
		else:
			if d_endpoints[d_endpoint] > 0: used_areas[d_endpoint] = False

	return used_areas