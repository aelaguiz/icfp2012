import inspyred
import pp
import random
import copy
import map
import eval

startMap = None
#moves = [map.MOVE_UP,map.MOVE_DOWN,map.MOVE_RIGHT,map.MOVE_LEFT]
moves = [map.MOVE_UP,map.MOVE_DOWN,map.MOVE_RIGHT,map.MOVE_LEFT,map.MOVE_ABORT]
#moves = [map.MOVE_UP,map.MOVE_DOWN,map.MOVE_RIGHT,map.MOVE_LEFT,map.MOVE_WAIT,map.MOVE_ABORT]

def fixed_generator(random, args):
    return [ random.choice(moves) for i in range(0, args['path_len']) ]

def var_generator(random, args):

    return [ random.choice(moves) for i in\
            range(random.randint(1, args['path_len'])) ]

def evaluator(candidates, args):
    return [eval.evalScore(c, args['map']) for c in candidates]

def trim_mutation(random, candidate, args):
    res = []
    for c in candidate:
        res.append(c)
        if c == map.MOVE_ABORT:
            if len(res) == 0:
                 return trim_mutation(random, generator(random, args), args)

            return res

    return candidate

def random_subtraction_mutation(random, candidate, args):
    mut_rate = args.setdefault('subtraction_rate', 0.1)
    max_remove = args.setdefault('max_subtraction_len', 4)

    if random.random() < mut_rate:
        maxLen = min(len(candidate)-1, max_remove)

        if maxLen >= 1:
            num = random.randint(0, maxLen)
            if num > 0:
                spot = random.randint(0, len(candidate)-1-num)

                left = candidate[0:spot]
                    
                #print candidate

                if(spot+1 < len(candidate)):
                    candidate = left + candidate[spot+1:]
                else:
                    candidate = left

                #print "Sub", candidate, "".join(candidate)
                #print candidate

    return candidate

def random_addition_mutation(random, candidate, args):
    mut_rate = args.setdefault('addition_rate', 0.1)

    if random.random() < mut_rate:
        maxLen = min(args['path_len']-len(candidate),\
                    args.setdefault('max_addition_len', 10))
        if maxLen > 0:
            print "Before", "".join(candidate)
            new = [ random.choice(moves) for i in\
                    range(random.randint(1, maxLen)) ]
            spot = random.randint(0, len(candidate)-1)

            candidate = candidate[:spot] + new + candidate[spot:]
            #print "Add", candidate
            print "After", "".join(candidate)

        #for i, m in enumerate(candidate):
            #if random.random() < rate:
                #candidate[i] = random.choice(moves)

    return candidate

def random_reset_mutation(random, candidate, args):
    mut_rate = args.setdefault('mutation_rate', 0.1)
    rate = args.setdefault('random_rate', 0.1)

    if random.random() < mut_rate:
        for i, m in enumerate(candidate):
            if random.random() < rate:
                candidate[i] = random.choice(moves)

    return candidate

def archiver(random, population, archive, args):
    new_archive = archive
    
    best = population[0]
    for ind in population:
        if ind > best:
            best = ind
        if len(new_archive) == 0:
            new_archive.append(ind)
        else:   
            should_remove = []
            should_add = True
            for a in new_archive:
                if a > best:
                    best = a

                if ind.candidate == a.candidate:
                    should_add = False
                    break
                elif ind < a:
                    should_add = False
                elif ind > a:
                    should_remove.append(a)
            for r in should_remove:
                new_archive.remove(r)
            if should_add:
                new_archive.append(ind)

    #print new_archive 

    #print best
    eval.evalScore(best.candidate, startMap, True)

    return new_archive

def ga(map):
    global startMap
    startMap = map

    ea = inspyred.ec.GA(random)
    ea.observer = inspyred.ec.observers.stats_observer
    ea.terminator = inspyred.ec.terminators.generation_termination
    ea.archiver = archiver
    ea.variator = [inspyred.ec.variators.crossovers.n_point_crossover,
            inspyred.ec.variators.mutator(random_reset_mutation)]
    #ea.variator = [inspyred.ec.variators.crossovers.n_point_crossover,
            #inspyred.ec.variators.mutator(random_reset_mutation), \
            #inspyred.ec.variators.mutator(random_subtraction_mutation),\
            #inspyred.ec.variators.mutator(random_addition_mutation),\
            #inspyred.ec.variators.mutator(trim_mutation) ]
    #print ea.variator
    #ea.replacer = inspyred.ec.replacers.steady_state_replacement

    eaArgs = dict()
    eaArgs['generator'] = fixed_generator
    #eaArgs['evaluator'] = evaluator
    eaArgs['terminator'] = inspyred.ec.terminators.generation_termination
    #eaArgs['evaluator'] = evaluator
    eaArgs['evaluator'] = inspyred.ec.evaluators.parallel_evaluation_pp
    eaArgs['pp_evaluator'] = evaluator
    eaArgs['pp_nprocs'] = 16
    eaArgs['pp_modules'] = ('eval', 'map')
    eaArgs['map'] = map
    eaArgs['path_len'] = 30
    eaArgs['maximize'] = True
    eaArgs['pop_size'] = 100
    eaArgs['max_generations'] = 100000

    eaArgs['crossover_rate'] = 1
    eaArgs['num_crossover_points'] = 4

    eaArgs['mutation_rate'] = 0.5

    eaArgs['subtraction_rate'] = 0.1
    eaArgs['max_subtraction_len'] = 15

    eaArgs['addition_rate'] = 0.1
    eaArgs['max_addition_len'] = 12

    eaArgs['random_rate'] = 0.2
    eaArgs['num_elites'] = 5
    
    ea.evolve(**eaArgs)
    print ea.archive
