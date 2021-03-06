#!/usr/bin/env python

import uuid
import random
import json


class Person():
    """
    Generate individuals
    """

    def __init__(self, padre=None, madre=None, generacion=0):
        #self.reset()
        self.dni = str(uuid.uuid4())
        self.sex = random.choice(['F','M'])
        self.pareja_con = None
        self.sons = set()
        self.padre = padre
        self.madre = madre
        self.generacion = generacion
        self.fingerprinted = False

    def hechar_cria(self, conyuge, cantidad=1):
        # Check sex
        nuevos_hijos = set()
        nuevos_hijos_dni = set()
        if self.sex == conyuge.sex:
            return nuevos_hijos
        # Distinto sexo pueden tener cria
        else:
            # Crear hijos
            if self.sex == 'M':
                padre = self.dni
                madre = conyuge.dni
            else:
                padre = conyuge.dni
                madre = self.dni
            for x in range(0,cantidad):
                np = Person(padre,madre,generacion=self.generacion+1)
                nuevos_hijos.add(np)
                nuevos_hijos_dni.add(np.dni)

            self.sons = self.sons.union(nuevos_hijos_dni)
            conyuge.sons = conyuge.sons.union(nuevos_hijos_dni)
            self.pareja_con = conyuge.dni
            return nuevos_hijos

    def __str__(self):

        return "Generacion: %s; DNI: %s; Sexo: %s"%(self.generacion,self.dni, self.sex) 

class Population():
    """
    Generate population with different characteristics
    """

    def __init__(self, cantidad):
        self.population = set()
        for x in range(cantidad):
            self.population.add(Person())

    def index(self, dni):
        for x in self.population:
            if x.dni==dni:
                return x
        raise IndexError


    def make_new_f(self, fertility_rate=.85, base_pop=100,nro_crias=2):
        new_f = set()
        # Cuento el sexo de menor representatividad
        f = 0
        m = 0
        for x in base_pop:
            f += 1 if x.sex=='F' else 0
        m = len(base_pop) - f
        menor_rep = ('F', f) if m>f else ('M', m)
        # Genero subconjunto de menor_rep
        conj_menor_rep = set()
        conj_mayor_rep = set()
        for x in base_pop:
            if x.sex==menor_rep[0]:
                conj_menor_rep.add(x)
            else:
                conj_mayor_rep.add(x)

        # Get number of couples with sons
        persons_with_sons = int(menor_rep[1]*fertility_rate)

        for x in range(persons_with_sons):
            p1 = conj_menor_rep.pop()
            p2 = conj_mayor_rep.pop()
            new_f = new_f.union(p1.hechar_cria(p2,nro_crias))
        self.population = self.population.union(new_f)
        return new_f

    def _son_covered_rec(self,person):
        if person.sons:
            for p in person.sons:
                self.covered.add(p)
                self._son_covered_rec(self.index(p))
        else:
            return None
    
    def _parents_covered_rec(self,person):
        if person.padre and person.madre:
            parents = person.padre, person.madre
            for p in parents:
                self.covered.add(p)
                self._parents_covered_rec(self.index(p))
        else:
            return None

    def _silbing_covered(self,person):
        if person.padre:
            for p in self.index(person.padre).sons:
                self.covered.add(p)


    def get_coverage(self, population):
        all_pop_len = len(population)
        self.covered = set()
        for x in population:
            if x.fingerprinted == True:
                # The subject is always part covered population
                self.covered.add(x.dni)
                self._son_covered_rec(x)
                self._parents_covered_rec(x)
                self._silbing_covered(x)
        coverage = round((float(len(self.covered))/all_pop_len)*100,2)
        return coverage



    def __str__(self):
        return "Amount: %s"%len(self.population)


def make_new_pop(n_pop,f_rate,max_sons):
    p = Population(n_pop)
    f1 = p.make_new_f(f_rate, p.population,max_sons)
    ori_and_f1 = p.population.union(f1)
    f2 = p.make_new_f(f_rate,f1,max_sons)
    return p, p.population | f1 | f2

def separate_sex(pop):
    all_together_f = set()
    all_together_m = set()
    for x in pop:
        if x.sex=='F':
            all_together_f.add(x)
        else:
            all_together_m.add(x)
    return all_together_f, all_together_m


def put_fingerprint(fingerprinted_f_rate, fingerprinted_m_rate):
    fingerprinted_f_rate = float(f)/100
    fingerprinted_m_rate = float(m)/100
    sample_f_size = int(len(all_together_f)*fingerprinted_f_rate)
    fingerprinted_f_pop = random.sample(all_together_f,  sample_f_size)
    for x in fingerprinted_f_pop:
        x.fingerprinted = True
    sample_m_size = int(len(all_together_m)*fingerprinted_m_rate)
    fingerprinted_m_pop = random.sample(all_together_m,  sample_m_size)
    for x in fingerprinted_m_pop:
        x.fingerprinted = True    
    return None

def avg_coverage(f,m,pop,n):
    return None

with open("input.js") as jsfile:
    cfg = json.load(jsfile)


for f in range(cfg["f_range_min"],cfg["f_range_max"],5):
    for m in range(cfg["m_range_min"],cfg["m_range_max"],5):
        if m>=f:
            pass
        else:
            coverage = set()
            for n in range(cfg['repe']):        
                p, all_together = make_new_pop(cfg['p_nbr'], cfg['fertility_rate'], 
                                               cfg['max_sons'])
                all_together_f, all_together_m = separate_sex(all_together)
                put_fingerprint(f, m)
                coverage.add(p.get_coverage(all_together))
            avrage_cov = sum(coverage)/cfg['repe']
            print f,m,avrage_cov


