globals [     ; declaring global variables and describing sliders
    ; presets ; choose presets of manual input using sliders for p,q,r (probabilities)
    ; normal  ; use of normal distribution for characteristics, set using switch [ true false ]
    ; r-p     ; probability of stimuli, set using a slider [ 1 .. 1000 ]
    rrp       ; variable as actually used, so that can easily have presets
    ; r-q     ; probability of interaction, set using a slider [ 1 .. 1000 ]
    rrq       ; variable as actually used, so that can easily have presets
    ; r-r     ; probability of moving, set using a slider [ 1 .. 1000 ]
    rrr       ; variable as actually used, so that can easily have presets
    agentnum  ; number of agents to create, currently set at beginning of setup
    ; sneed   ; slider value for needed if set manually  [ 0 .. 100 ]
    needed    ; time needed in community until an agent can become eligible
    selig     ; percentage of population not eligible to participate (initial)
    sduty     ; percentage of population feeling a duty to vote (initial)
    time      ; time: number of rounds (*/* assumed to be 1 week)
    affected  ; which one of the characteristics are affected by stimuli (list)
    ; a1 a2 a3 a4 a5 ; characteristics affected by stimuli, these variables are not necessary as such, since
    ; setting the bn to 0.5 has the same effect on average; however, the switches offer a quick and easy way
    ; to turn on / off stimuli, hence this way  [ true false ]
    ; b1 b2 b3 b4 b5 ; stimuli work up or down? [ 0.0 .. 1.0 ]
    ]

breed [ pagents pagent ]
  ; I don't want to refer to turtles all the time
  ; pagents = participation agents to keep NetLogo 6 happy

pagents-own [  ; declaring variables unique to agents
    history   ; list of levels (history)
    rnorm     ; random variable needed for setup
    level     ; level of participation [ 0 .. 12 ]
    active    ; agent is active (passive)  [ 1 .. 5 ]
    overt     ; agent is overt (covert)  [ 1 .. 5 ]
    auton     ; agent is autonomous (compliant)  [ 1 .. 5 ]
    approach  ; agent is approaching (avoiding)  [ 1 .. 5 ]
    contin    ; agent is continuous (episodic)  [ 1 .. 5 ]
    taking    ; agent is outtaking (inputting)  [ 1 .. 5 ]
    express   ; agent is expressive (instrumental)  [ 1 .. 5 ]
    social    ; agent is social (nonsocial)  [ 1 .. 5 ]
    eligible  ; agent is eligible to participate [ 0 1 ]
    duty      ; agent feels duty to participate [ 0 1 ]
    SES       ; socioeconomic status  [ 1 .. 3 ]
    contacts  ; number of people known in community
    spent ]   ; time spent in community

to setup ; setting up the simulation
  ; **INITIALIZING **
  ;; (for this model to work with NetLogo's new plotting features,
  ;; __clear-all-and-reset-ticks should be replaced with clear-all at
  ;; the beginning of your setup procedure and reset-ticks at the end
  ;; of the procedure. However, I don't use ticks to track time)
  __clear-all-and-reset-ticks                   ; clear everything to start
    set agentnum 100     ; number of agents to create: size of community (*/*)
    set selig 3          ; 3% not eligible to start with
    set sduty 20         ; 20% feel a duty to vote to start with
    set-histogram-num-bars 12   ; setup histogram of levels
    action               ; initial setting of political environment, can be changed
                         ; using the Action button during the simulation to study the
                         ; effects of shocks etc.

    ; **CREATE AGENTS**
    create-pagents agentnum          ; create agents, number set above
    ask pagents [setxy  (random world-width) (random world-height)] ; eye candy: spread out
    ;; note that space has no meaning in this model

    ; **INITIAL DISTRIBUTIONS** : characteristics and levels of the agents, set using a slider
    ask pagents [ set level 0        ; all apathetics
                 set spent 0        ; start as newcomers
                 set contacts 0     ; with no contacts so far
                 set history [ ] ]  ; no history of involvement levels
    colorize ; eye candy: set colour of agents according to level of involvement

    ; **SET CHARACTERISTICS ** : a choice, set using switch
    ifelse normal = true [ ; set characteristics following a (*/*) normal distribuion
        ask pagents [
            randomize    ; get random values according to normal distribution
            set active   rnorm ; [ 1 .. 5 ]
            randomize
            set overt    rnorm
            randomize
            set auton    rnorm
            randomize
            set approach rnorm
            randomize
            set contin   rnorm
            randomize
            set taking   rnorm
            randomize
            set express  rnorm
            randomize
            set social   rnorm
        ] ]
        [ ; set characteristics (*/*) randomly
          ask pagents  [
              set active   random 5 + 1 ; [ 1 2 3 4 5 ] ; @@@ These probably could be related to random-float values
              set overt    random 5 + 1
              set auton    random 5 + 1
              set approach random 5 + 1
              set contin   random 5 + 1
              set taking   random 5 + 1
              set express  random 5 + 1
              set social   random 5 + 1
        ] ]
    ask pagents [ ; this part is the same whether randomly or normally distributed
        set eligible 0
        if random 100 > selig [ set eligible 1 ] ; selig % are not eligible (3% set above)
                                                 ; ****** this should probably be moved to the presets section
                                                 ; so that repressive states (etc.) can affect this variable, too.
                                                 ; alternatively, run this command again with some of the presets,
                                                 ; now of course with a different value (i.e. not selig)... ******
        if random 100 < sduty [ set duty     1 ] ; sduty % feel duty (20% set above)
        set SES random 3 + 1 ] ; [ 1 .. 3 ]

    set time 1                           ; start at beginning; assumed time frame = 1 week
    plotting                             ; initial plotting
end

to go ; the basic procedure
    ; The stimuli are sent to all agents, the interaction/moving only affects a few
    ; agents a time. Using the probabilities, the single procedures can still be
    ; more or less turned off, by setting the probability to an extremely unlikely
    ; value (see presets).
    if random rrp = 0 [ ask pagents [ stimuli ] ]    ; sometimes all agents receive stimuli
    ask pagents [                          ; repeat for all agents (always)
        if random rrq = 0 [ interaction ] ; some interact with other agents
        if random rrr = 0 [ moving ]      ; some move
        updating ]                        ; update the levels of involvement
    colorize                              ; set colours of all agents according to level
    plotting                              ; plot the results after each round
    set time time + 1                     ; time passes, assumed to be one week (*/*),
end

to stimuli     ; stimuli are sent to all agents
    ; The characteristics affected are based on Milbrath's book.
    let magnitude 0

    if level > 0 [ ; apathetics are not affected since they are not exposed to stimuli
        ; 1) check if particular characteristic is affected (see presets)
        ; 2) calculate magnitude (*/*) of impact depending
        ;    on characteristics and political environment; 3) change.
        ; ***** think more about the magnitude against the time frame: what are realistic assumptions? *****
        if member? 5 affected [ set magnitude 3 * ( b5 - (random 2)) / ( auton + contin )
                                set active active + magnitude ]
        if member? 4 affected [ set magnitude 3 * ( b4 - (random 2)) / ( auton + contin )
                                set overt overt + magnitude ]
        if member? 3 affected [ set magnitude 3 * ( b3 - (random 2)) / ( auton + contin )
                                set contin contin + magnitude ]
        if member? 2 affected [ set magnitude 3 * ( b2 - (random 2)) / ( auton + contin )
                                set express express + magnitude ]
        if member? 1 affected [ set magnitude 3 * ( b1 - (random 2)) / ( auton + contin )
                                set taking taking + magnitude ]
        ; ***** can use the variable a1, a2, ... directly, and thus won't need the affected list *****
    ]
end

to interaction        ; some agents interact
  let partner 0       ; local variables
  let magnitude 0
  let magnitudeP 0
    ; impact of interaction on partner depending on characterstics
    ; 1) determine who interacts
    if ( social + (level / 3 + 1 ) + active + random-float 2.5 ) > 10 and level >= 3 [        ; initiate (*/*)
        set partner one-of turtles                                 ; partner = anyone (*/*) @@@ could set to neighbouring instead
        ;; the assumption is that we look at a single community, so space has no meaning at the moment (hence anyone).
        if [social] of partner + [active] of partner + [approach] of partner + random-float 2.5 > 10 and [level] of partner > 0 [   ; accept: interact (*/*)
                set magnitude (random 2 ) / ( auton + contin )
                if random 20 * SES = 0 [ set magnitude magnitude / 10 ]   ; cynical: less impact (*/*)
                set magnitudeP (random 2) / ( [auton] of partner + [contin] of partner )
                if random 20 * [SES] of partner = 0 [set magnitudeP magnitudeP / 10 ]
                ifelse approach > [approach] of partner [ask partner [set approach approach + magnitudeP ]]
                ; OLD: set [approach] of partner [approach] of partner + magnitudeP
                ; TRANSITION: set [<variable>] of <agent> <value> >>> ask <agent> [ set <variable> <value> ]
                ; TRANSITION: ask <agent> [ set <variable> [value] of myself ]
                                                      [set approach approach + magnitude ]
                if level > [level] of partner [ ask partner [set active active + magnitudeP
                                              set overt overt + magnitudeP ]]
                if level < [level] of partner [ set active active + magnitude
                                              set overt overt + magnitude ]
                ; ***** any more rules? *****
                set contacts contacts + 1                        ; add to contacts
                ask partner [set contacts contacts + 1 ] ; add to partner's contacts
                ]
        ]
end

to moving            ; some agents move
    set spent 0      ; new place: reset time
    set contacts 0   ; lose contacts
    setxy (random world-width) (random world-height) ; eye candy: move physically
end

to updating         ; update level of political involvement for all agents
    let done 0
   ; local variable to make sure level only set once
    set done false  ; i.e. level not yet determined

    ; check ranges to prevent illegal values for variables
    if active < 0 [ set active 0 ]
    if active > 5 [ set active 5 ]
    if overt < 0 [ set overt 0 ]
    if overt > 5 [ set overt 5 ]
    if auton < 0 [ set auton 0 ]
    if auton > 5 [ set auton 5 ]
    if approach < 0 [ set approach 0 ]
    if approach > 5 [ set approach 5 ]
    if taking < 0 [ set taking 0 ]
    if taking > 5 [ set taking 5 ]
    if express < 0 [ set express 0 ]
    if express > 5 [ set express 5 ]
    if social < 0 [ set social 0 ]
    if social > 5 [ set social 5 ]

    ifelse spent >= needed [ set eligible 1 ]   ; spent enough time in community
    [ set eligible 0 ]
    ; if no such law exists needed is 0 and agents will become eligible immediately
    ; after the move.

    ; start at bottom and see if criteria still met
    ; (*/*) assumed that move up if on average > 3 (i.e. above average on criteria)
    set level 0
    ; ***** currently there is no stochastic element to most rules, how big (magnitude) is it? *****
    if eligible = 1 [                     ; not eligible, not involved
        if random 10 = 0 [ set level 1 ]  ; exposed to stimuli, threshold (*/*)
        if duty = 1 [ set level 2 ]       ; will always vote if feel a duty to do so.
        ; level 2: voting, using characteristics;
        ifelse done = false and active + approach - (5 / 3) * SES > 3 [ set level 2 ]
        [ set done true ] ; did not pass threshold, will remain at level currently assigned
        ; level 3: discussion
        ifelse done = false and active + overt + approach + social + (2.5 * contacts ) / time  > 15 [ set level 3 ]
        [ set done true  ]
        ; level 4: button, party ID
        ifelse done = false and overt + express > 6 [ set level 4 ]
        [ set done true  ]
        ; level 5: contact official
        ifelse done = false and overt + auton + approach + taking > 12 [ set level 5 ]
        [ set done true  ]
        ; level 6: donates money
        ifelse done = false and active + approach - taking + express - social > 3 [ set level 6 ]
        [ set done true  ]
        ; level 7: attend rally
        ifelse done = false and overt + social + (2.5 * contacts ) / time > 9 [ set level 7 ]
        [ set done true  ]
        ; level 8: time in campaigning
        ifelse done = false and active + overt + approach + taking + express + (5 / 3) * SES > 18 [ set level 8 ]
        [ set done true  ]
        ; level 9: active member
        ifelse done = false and contin + express + (5 / 3) * SES > 9 [ set level 9 ]
        [ set done true  ]
        ; level 10: solicit funds
        ifelse done = false and active + overt + contin + (5 / 3) * SES > 12 [ set level 10 ]
        [ set done true  ]
        ; level 11: candidate -- it has been suggested that people are also sometimes *asked* to be candidated rather
        ; than volunteer; a fact which is actually catered for since people with the 'wrong' characteristics will
        ; decline such a request.
        ifelse done = false and active + overt + approach + contin + (2.5 * contacts) / time + (5 / 3) * SES > 18 [ set level 11 ]
        [ set done true  ]
        ; level 12: hold office -- particularly here, but actually with all levels, this procedure totally ignores the
        ; fact that the number of agents at each level may be limited by the system (i.e. political environment). For
        ; example, there may be more people wanting to / willing to hold office than places.
        if done = false and active + overt + auton + approach + contin - taking + (2.5 * contacts) / time + (5 / 3) * SES > 18 [ set level 12 ]
    ]
    set spent spent + 1                ; time passes
    set history sentence level history ; record levels of involvement for each agent
end

to plotting    ; plot results after each round
    set-current-plot "Levels"
        set-current-plot-pen "Gladiators"
            plot count pagents with [ level >= 8 ]               ; plot Gladiators
         set-current-plot-pen "Transitionals"
            plot count pagents with [ level >= 5 and level < 8 ] ; plot Transitionals
         set-current-plot-pen "Spectators"
            plot count pagents with [ level < 5 and level > 0 ]  ; plot Spectators
         set-current-plot-pen "Apathetics"
            plot count pagents with [ level = 0 ]                ; plot Apathetics
    set-current-plot "Hist" ; plot a histogram showing the distribution of the levels
        histogram [level] of pagents
        ; TRANSITION: color-of turtle 0  >>> [color] of turtle 0
end

to randomize ; create a random number between 100 and split according to a
    ; (*/*) normal distribution
    ; ***** the random-normal command doesn't give integers, but then again
    ; I don't need integers, try to use random-normal in the setup *****
    set rnorm random 100   ; random number [ 0 .. 99 ]
    if rnorm >= 0  and rnorm < 6  [ set rnorm 1 ] ; 6%
    if rnorm >= 6  and rnorm < 31 [ set rnorm 2 ] ; 25%
    if rnorm >= 31 and rnorm < 69 [ set rnorm 3 ] ; 38%
    if rnorm >= 69 and rnorm < 94 [ set rnorm 4 ] ; 25%
    if rnorm >= 94 [ set rnorm 5 ]                ; 6%
end

to colorize ; set colour of agents according to level (eye candy):
    ask pagents [ if level = 0 [ set color brown ]                      ; apathetic
                 if member? level [ 1 2 3 4 ] [ set color orange ]     ; spectators
                 if member? level [ 5 6 7 ] [ set color pink ]         ; transitionals
                 if member? level [ 8 9 10 11 12 ] [ set color red ] ] ; gladiators
end

to action
    ; This part of the setup is removed so that the environment can be changed whilst
    ; the simulation runs (Action button). This allows to study the effect of things like
    ; a close election where different (and more) stimuli are sent.

    ; **PRESETS**: set different political environments, set using sliders
    ; use manual (*/*) settings to start with, override accordingly
   if presets = "Manual" [ ; set everything manually, using the sliders on the left -- world
        set rrp r-p      ; stimuli
        set rrq r-q      ; interaction
        set rrr r-r      ; moving
        set needed sneed  ; time needed until eligible
        ]
    if presets = "Normal" [ ; an unexciting world with not much happening
        ; supposedly this is the world where shocks such as elections could be tried out against -- world
        set a1 true ; taking affected (*/*)
        set b1 .5   ; up or down (*/*)
        set a2 true ; express affected (*/*)
        set b2 .5   ; up or down (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .5   ; up or down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 .5   ; up or down (*/*)
        set a5 true ; active affected (*/*)
        set b5 .4   ; -.1 down (*/*)
        set rrp 8   ; every 8 week (*/*)
        set rrq 2   ; every 2 week (*/*)
        set rrr 260 ; moving every 5 years (*/*)
        set needed 4 ; time needed until eligible (*/*): 1 month (registration)
        ]
    if presets = "Repressive State" [ ; regime where dissent is discouraged -- (incomplete world)
        set a1 true ; taking affected (*/*)
        set b1 .5   ; up or down (*/*)
        set a2 true ; express affected (*/*)
        set b2 .3   ; -.2 down (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .4   ; -.1 down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 .3   ; -.2 down (*/*)
        set a5 true ; active affected (*/*)
        set b5 .5   ; up or down (*/*)
        set rrp 2   ; every 2 weeks (*/*)
        set rrq 4   ; every 4 weeks (*/*)
        ;set rrr 1  ; moving not affected (*/*)
        set needed 12 ; time needed until eligible (*/*): 12 weeks (3 months)
        ]
    if presets = "Random World" [ ; for fun / comparison, everything set (*/*) randomly -- world
        set a1 true ; taking affected (*/*)
        set b1 random-float 1.0   ; [ 0.00 .. 1.00 ]  (*/*)
        set a2 true ; express affected (*/*)
        set b2 random-float 1.0   ; [ 0.00 .. 1.00 ]  (*/*)
        set a3 true ; contin affected (*/*)
        set b3 random-float 1.0   ; [ 0.00 .. 1.00 ]  (*/*)
        set a4 true ; overt affected (*/*)
        set b4 random-float 1.0   ; [ 0.00 .. 1.00 ]  (*/*)
        set a5 true ; active affected (*/*)
        set b5 random-float 1.0      ; [ 0.00 .. 1.00 ]  (*/*)
        set rrp random 4 + 1   ; every [ 1 .. 4 ] weeks (*/*)
        set rrq random 4 + 1   ; every [ 1 .. 4 ] weeks (*/*)
        set rrr random 500 + 1 ; every ~5 years (*/*)
        set needed random 52 ; time needed until eligible (*/*): max 1 year
        ]
    if presets = "Frequent Movers" [ ; inner city where people move in and out a lot -- (incomplete world)
        set a1 true ; taking affected (*/*)
        set b1 .6   ; +.1 up (*/*)
        set a2 true ; express affected (*/*)
        set b2 .4   ; -.1 down (*/*)
        set a3 false ; contin not affected (*/*)
        set a4 false ; overt not affected (*/*)
        set a5 false ; active not affected (*/*)
        ; set rrp 2 ; not affected (*/*)
        ; set rrq 4 ; not affected (*/*)
        set rrr 52  ; moving every ~1 year (*/*)
        set needed sneed ; time needed until eligible (*/*): manually
        ]
    if presets = "No Movers" [ ; people don't move, virtual (*/*) for testing -- (incomplete world)
        set a1 true ; taking affected (*/*)
        set b1 .5   ; up or down (*/*)
        set a2 true ; express affected (*/*)
        set b2 .5   ; up or down (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .51  ; +.01 up (*/*)
        set a4 false ; overt not affected (*/*)
        set a5 false ; active not affected (*/*)
        ; set rrp 2 ; not affected (*/*)
        ; set rrq 4 ; not affected (*/*)
        set rrr 999999999  ; no moving (*/*)
        set needed 0 ; time needed until eligible (*/*): 0 (no movers: no point for this variable)
        ]
    if presets = "Election" [ ; an election is about to happen -- event
        set a1 true ; taking affected (*/*)
        set b1 .5   ; up or down (*/*)
        set a2 true ; express affected (*/*)
        set b2 .1   ; +.1 up (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .4   ; -.1 down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 .6   ; +.1 up (*/*)
        set a5 true ; active affected (*/*)
        set b5 .5   ; up or down (*/*)
        set rrp 1   ; every 1 week (*/*)
        set rrq 2   ; every 2 week (*/*)
        ;set rrr 1  ; moving not affected (*/*)
        ]
    if presets = "Close Election" [ ; an election where the result is rather unclear --event
        set a1 true ; taking affected (*/*)
        set b1 .4   ; -.1 down (*/*)
        set a2 true ; express affected (*/*)
        set b2 .7   ; +.2 up (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .4   ; -.1 down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 .7   ; +.2 up (*/*)
        set a5 true ; active affected (*/*)
        set b5 .6   ; +.1 up (*/*)
        set rrp 1   ; every 1 week (*/*)
        set rrq 1   ; every 1 week (*/*)
        ;set rrr 1  ; moving not affected (*/*)
        ]
    if presets = "Assassination" [ ; assassination of a popular leader -- event
        set a1 true ; taking affected (*/*)
        set b1 .5   ; up or down (*/*)
        set a2 true ; express affected (*/*)
        set b2 1    ; +.5 up (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .3   ; -.2 down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 1    ; +.5 up (*/*)
        set a5 true ; active affected (*/*)
        set b5 1   ; +.5 up (*/*)
        set rrp 1   ; every 1 week (*/*)
        set rrq 1   ; every 1 week (*/*)
        ;set rrr 1  ; moving not affected (*/*)
        ]
    if presets = "Dictatorship" [ ; dictatorship with no tolerance of oposition -- world
        set a1 true ; taking affected (*/*)
        set b1 .6   ; +.1 up (*/*)
        set a2 true ; express affected (*/*)
        set b2 .3   ; -.2 down (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .2   ; -.3 down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 .3   ; -.2 down (*/*)
        set a5 true ; active affected (*/*)
        set b5 .4   ; -.1 down (*/*)
        set rrp 1   ; every 1 week (*/*)
        set rrq 8   ; every 8 week (*/*)
        set rrr 260 ; moving every 5 years (*/*)
        set needed 26 ; time needed until eligible (*/*): half a year
        ]
    if presets = "Hard Times" [ ; people work hard to get by, little time for politics -- world
        set a1 true ; taking affected (*/*)
        set b1 .1   ; +.1 up (*/*)
        set a2 true ; express affected (*/*)
        set b2 .5   ; up or down (*/*)
        set a3 true ; contin affected (*/*)
        set b3 .4   ; -.1 down (*/*)
        set a4 true ; overt affected (*/*)
        set b4 .5   ; up or down (*/*)
        set a5 true ; active affected (*/*)
        set b5 .5   ; up or down (*/*)
        set rrp 2   ; every 2 week (*/*)
        set rrq 25  ; every half year (*/*)
        set rrr 260 ; moving every 5 years (*/*)
        set needed 12 ; time needed until eligible (*/*): 3 months, has no time to register before
        ]
    if presets = "Stimuli Only" [        ; only stimuli can happen, virtual (*/*) -- for testing
        set rrp 1         ; always       ; other values as set manually (unaffected)
        set rrq 999999999 ; off
        set rrr 999999999 ; off
        set needed 0 ]
    if presets = "Interaction Only" [    ; only interaction can happen, virtual (*/*) -- for testing
        set rrp 999999999 ; off          ; other values as set manually (unaffected)
        set rrq 1         ; always
        set rrr 999999999 ; off
        set needed 0 ]

    ; ***** need to add more presets here *****
    ; the presets need backup from literature where possible, both in qualitative and quantitative terms

    ; ***** the following few lines are redundant: change the stimuli to check a1, a2, ... directly,
    ; there is no need for a list. *****
    set affected [ ] ; which characteristics are affected by the stimuli?
    if a1 = true [ set affected sentence 1 affected ] ; add to list of affected characteristics
    if a2 = true [ set affected sentence 2 affected ] ; set using switches
    if a3 = true [ set affected sentence 3 affected ]
    if a4 = true [ set affected sentence 4 affected ]
    if a5 = true [ set affected sentence 5 affected ]
end

to exportdata ; this procedure exports the history of all agents to a text file which can
    ; then be opened in a spreadsheet programme for data analysis
    let i 0
                      ; count variable
    clear-output                    ; in case something was exported before
    set i 0
    repeat agentnum [               ; for all agents
        print [history] of turtle i
        set i i + 1 ]
    export-output "ppart.txt"       ; write to file
end
@#$#@#$#@
GRAPHICS-WINDOW
760
10
974
225
-1
-1
5.9
1
10
1
1
1
0
1
1
1
-17
17
-17
17
0
0
1
ticks
30.0

BUTTON
179
10
234
43
Setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
234
10
289
43
Go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
234
43
289
76
Steps
repeat n [ go ]
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
20
11
170
38
Setup and start simulation ->
9
75.0
0

SLIDER
4
147
175
180
r-p
r-p
1
1000
3.0
1
1
Stimuli
HORIZONTAL

SLIDER
3
180
175
213
r-q
r-q
1
1000
2.0
1
1
Interaction
HORIZONTAL

SLIDER
4
213
175
246
r-r
r-r
1
1000
737.0
1
1
Moving
HORIZONTAL

TEXTBOX
8
280
184
358
^-- Setting the probabilities for the different procedures: set manually or choose a preset political environment. Once every x. (these sliders are not responsive to the presets, see code)
9
75.0
0

CHOOSER
4
102
175
147
presets
presets
"Manual" "Normal" "Repressive State" "Random World" "Stimuli Only" "Interaction Only" "Frequent Movers" "No Movers" "Close Election" "Election" "Assassination" "Dictatorship" "Hard Times"
10

PLOT
600
10
760
247
Levels
Time
Number
0.0
5.0
0.0
5.0
true
false
"" ""
PENS
"Gladiators" 1.0 0 -2674135 true "" ""
"Transitionals" 1.0 0 -2064490 true "" ""
"Spectators" 1.0 0 -955883 true "" ""
"Apathetics" 1.0 0 -6459832 true "" ""
"Voters" 1.0 0 -10899396 true "" ""

SWITCH
299
17
402
50
normal
normal
0
1
-1000

TEXTBOX
303
57
423
101
^- Assume normal distribution of characteristics.
9
75.0
0

SLIDER
4
245
175
278
sneed
sneed
0
100
0.0
1
1
Eligible Time
HORIZONTAL

TEXTBOX
663
36
760
92
Gladiators: red\nTransitionals: pink\nSpectators: orange\nApathetics: brown
9
4.0
1

BUTTON
475
259
601
292
Check Agent Smith
inspect turtle 4
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
179
43
234
76
Action
action
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
19
29
161
101
Stop simulation and use action button to change political environment on the fly. -->\nChoose number of steps. -->\nPolitical environments --v
9
75.0
0

PLOT
411
10
600
247
hist
NIL
NIL
0.0
13.0
0.0
5.0
true
false
"" ""
PENS
"default" 1.0 1 -16777216 true "" ""

TEXTBOX
441
230
593
248
 0  1 2 3  4 5 6  7 8 9 0 12
11
0.0
0

BUTTON
663
260
760
293
Export Data
exportdata
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SWITCH
179
113
269
146
a1
a1
0
1
-1000

SWITCH
179
146
269
179
a2
a2
0
1
-1000

SWITCH
179
179
269
212
a3
a3
0
1
-1000

SWITCH
179
212
269
245
a4
a4
0
1
-1000

SWITCH
179
245
269
278
a5
a5
0
1
-1000

SLIDER
269
113
411
146
b1
b1
0
1
0.5
0.1
1
Tak
HORIZONTAL

SLIDER
269
146
411
179
b2
b2
0
1
1.0
0.1
1
Exp
HORIZONTAL

SLIDER
269
179
411
212
b3
b3
0
1
0.3
0.1
1
Cnt
HORIZONTAL

SLIDER
269
212
411
245
b4
b4
0
1
1.0
0.1
1
Ovt
HORIZONTAL

SLIDER
269
245
411
278
b5
b5
0
1
1.0
0.1
1
Act
HORIZONTAL

TEXTBOX
186
282
419
338
^-- Turn on/off stimuli and their magnitude. Outtaking (tak), expressive (exp), continuous (cnt), overt (ovt), active (act): 0 for negative impact, 1 for positive.
9
75.0
1

SLIDER
179
76
289
109
n
n
1
100
24.0
1
1
Steps
HORIZONTAL

MONITOR
411
247
468
292
Weeks
time
0
1
11

@#$#@#$#@
# A Simulation of Political Participation
This simulation models political participation after Milbrath (1965). I wrote the model in 2005 as part of my MSc thesis. The only changes in the code since were to make the model work in NetLogo 5 and NetLogo 6. Moreover, more extensive documentation is provided in the NetLogo file (both here in the "info" tab, and as comments in the code).

## Overview
### Purpose
Examine whether the description of political participation outlined in Milbrath (1965) is a realistic description of political participation. Milbrath provides an detailed description on how and why individuals participated in politics. The aim here is to check whether the descriptions in Milbrath add up to observed patterns of political participation.

The focus is on the different levels of participation, and not on vote choice and other related concepts. The main test is to check whether the dynamics of political participation occur. Furthermore, the impact of different political environments and the role of social contacts was also at the back of the mind when writing this model.

### Entities, state variables, and scales
Milbrath's model of political participation was simplified. There are agents and global variables; patches do not play a role. Agents have individual characteristics, which are -- with the exception of _felt duty_ -- open to change according to the dynamics of the system. These changes depend on the characteristics of the individuals. The characteristics are (opposites in square brackets): active [passive], overt [covert], autonomous [compliant], approaching [avoiding], continuous [episodic], outtaking [inputting], expressive [instrumental], and social [nonsocial]. Each characteristic is modelled as a continuous variable. Agents also have a specific socio-economic status (SES), contacts in the community, and time is tracked to determine the time agents have spent in a community. All variables are modelled as continuous variables, except for _duty_ and _eligibility_ (binary), and _time_ and _contacts_ (whole numbers).
Political participation is represented in levels, ranging from 0 (apathetic) to 12 (holding office).

### Process overview and scheduling
After the setup, agents are subject to stimuli with probability _p_, then interact with other agents with probability _q_, and then move to another community with probability _r_. Levels of political participation are updated at the end of each round, assumed to be 1 week. The values of p, q, and r are determined by the political environment (put differently, the political environment is determined by p, q, and r). Agents keep a history of their level of political participation.

## Design concepts
### Basic principles
The simulation implements a simplified version of the model of political participation presented in Milbrath (1965). It implements the idea that both the environment and interpersonal interaction affects individuals' propensity to participate, while both are moderated by individual characteristics.

### Emergence
The level of political participation is determined by a set of rules, but is a result of individual characteristics, the political environment, as well as the nature of interpersonal interaction. Depending on how these variables are changed, the patterns of political participation change. These patterns of participation do not emerge when parts of the model are turned off (e.g. no interpersonal interaction).

### Adaptation
The agents do not have adaptive behaviour. Their actions are determined by global variables (p, q, r) as well as individual characteristics. The level of participation is determined following a set of rules, thus making the assumption that individuals with a given propensity to participate actually have the opportunity to participate. For example, in the model there are no limits on the number of individuals who could hold and office.

### Objectives
The agents do not have a particular objective, but will participate in politics if they can. The decision to participate considers the state variables of the agents.

### Learning
The agents do not learn, but the interpersonal interaction can change most of the individual characteristics.

### Prediction
Agents have no sense of time.

### Sensing
When agents interact with other agents, they do so quite intensively, affecting each other in most state variables. For agents, the environment exists only in the sense that it sends stimuli.

### Interaction
Agents interact directly with each other, affecting each other's states. Whether agents initiate interaction depends on their sociability and overtness. Interaction is with a random other agents. The impact agents have on each other depends on individual characteristics.

### Stochasticity
Most aspects of the model include stochasticity to include the probabilistic nature of human behaviour without modelling the underlying causes thereof.

### Collectives
There are no real collectives. Communities exist only as a variable of individual agents. Agents are assumed to be member of a community, and after each round they have spent more time in that community -- unless they move. All contacts they have are assumed to be within the community. When they move, their contacts are reset. The underlying assumption is that the simulated agents form a single community. If an agent is set to move, this is as if it moves to a different community, and at the same time a new agent moves to the community in question. This way, there is no need to model communities explicitly.

### Observation
The main output is the distribution of agents into different levels of participation: How many agents participate in politics to what level.

## Details
### Initialization
Initialization necessitates that a political environment is set, either from the presets or via the sliders for p, q, and r.

### Input data
No data are input; agents and their characteristics are generated randomly.

### Submodels
There are submodels for (1) stimuli from the political environment, (2) interaction with other agents, (3) moving to another community, and (4) updating. Separate submodels colorize agents according to their level of participation and plot.

## Additional information
### Further model description in
- Ruedin, D. 2007. "Testing Milbrath’s 1965 Framework of Political Participation: Institutions and Social Capital." _Contemporary Issues and Ideas in Social Sciences_ 3(3).
- Ruedin, D. 2005. "A Simulation of Political Participation." _MSc Thesis_. Oxford University.

### Code also used in
- Ruedin, D. 2011. "The role of social capital in the political participation of immigrants: Evidence from agent-based modelling." SFM Discussion Paper 27.

### Reference
- Milbrath, L. (1965) _Political Participation: How and Why Do People Get Involved in Politics?_, Chicago. Rand McNally.

### Version
Original version: 20 May 2005.
Upgraded to NetLogo 4.1.1: 20 April 2011.
Additional comments and information: 5 September 2012.
ODD description and yet more comments: 22 March 2014, 12 April 2014.
Updated to NetLogo 6.1.1:  14 April 2020.
Now using MIT Licence:  14 April 2020.

### Licence
MIT https://opensource.org/licenses/MIT

Copyright 2020 Didier Ruedin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Note on hard-coded numbers
Numbers that are assumed are declared using */* in the comments, other numbers are backed by some data/literature.

## Known limitations and comments
- "Check Agent Smith" is implemented to monitor turtle 4 (could be any turtle).
- Export only works when called manually.
- Some presets are purely for testing.
- Some values of presets have not yet been checked against the literature.
- Presets are possibly still incomplete.
- Some open tasks remaining (indicated with asterisks ****)
- The model should probably use random-normal rather than its own code to generate normally distributed values
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

ant
true
0
Polygon -7500403 true true 136 61 129 46 144 30 119 45 124 60 114 82 97 37 132 10 93 36 111 84 127 105 172 105 189 84 208 35 171 11 202 35 204 37 186 82 177 60 180 44 159 32 170 44 165 60
Polygon -7500403 true true 150 95 135 103 139 117 125 149 137 180 135 196 150 204 166 195 161 180 174 150 158 116 164 102
Polygon -7500403 true true 149 186 128 197 114 232 134 270 149 282 166 270 185 232 171 195 149 186
Polygon -7500403 true true 225 66 230 107 159 122 161 127 234 111 236 106
Polygon -7500403 true true 78 58 99 116 139 123 137 128 95 119
Polygon -7500403 true true 48 103 90 147 129 147 130 151 86 151
Polygon -7500403 true true 65 224 92 171 134 160 135 164 95 175
Polygon -7500403 true true 235 222 210 170 163 162 161 166 208 174
Polygon -7500403 true true 249 107 211 147 168 147 168 150 213 150

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

bee
true
0
Polygon -1184463 true false 151 152 137 77 105 67 89 67 66 74 48 85 36 100 24 116 14 134 0 151 15 167 22 182 40 206 58 220 82 226 105 226 134 222
Polygon -16777216 true false 151 150 149 128 149 114 155 98 178 80 197 80 217 81 233 95 242 117 246 141 247 151 245 177 234 195 218 207 206 211 184 211 161 204 151 189 148 171
Polygon -7500403 true true 246 151 241 119 240 96 250 81 261 78 275 87 282 103 277 115 287 121 299 150 286 180 277 189 283 197 281 210 270 222 256 222 243 212 242 192
Polygon -16777216 true false 115 70 129 74 128 223 114 224
Polygon -16777216 true false 89 67 74 71 74 224 89 225 89 67
Polygon -16777216 true false 43 91 31 106 31 195 45 211
Line -1 false 200 144 213 70
Line -1 false 213 70 213 45
Line -1 false 214 45 203 26
Line -1 false 204 26 185 22
Line -1 false 185 22 170 25
Line -1 false 169 26 159 37
Line -1 false 159 37 156 55
Line -1 false 157 55 199 143
Line -1 false 200 141 162 227
Line -1 false 162 227 163 241
Line -1 false 163 241 171 249
Line -1 false 171 249 190 254
Line -1 false 192 253 203 248
Line -1 false 205 249 218 235
Line -1 false 218 235 200 144

bird1
false
0
Polygon -7500403 true true 2 6 2 39 270 298 297 298 299 271 187 160 279 75 276 22 100 67 31 0

bird2
false
0
Polygon -7500403 true true 2 4 33 4 298 270 298 298 272 298 155 184 117 289 61 295 61 105 0 43

boat1
false
0
Polygon -1 true false 63 162 90 207 223 207 290 162
Rectangle -6459832 true false 150 32 157 162
Polygon -13345367 true false 150 34 131 49 145 47 147 48 149 49
Polygon -7500403 true true 158 33 230 157 182 150 169 151 157 156
Polygon -7500403 true true 149 55 88 143 103 139 111 136 117 139 126 145 130 147 139 147 146 146 149 55

boat2
false
0
Polygon -1 true false 63 162 90 207 223 207 290 162
Rectangle -6459832 true false 150 32 157 162
Polygon -13345367 true false 150 34 131 49 145 47 147 48 149 49
Polygon -7500403 true true 157 54 175 79 174 96 185 102 178 112 194 124 196 131 190 139 192 146 211 151 216 154 157 154
Polygon -7500403 true true 150 74 146 91 139 99 143 114 141 123 137 126 131 129 132 139 142 136 126 142 119 147 148 147

boat3
false
0
Polygon -1 true false 63 162 90 207 223 207 290 162
Rectangle -6459832 true false 150 32 157 162
Polygon -13345367 true false 150 34 131 49 145 47 147 48 149 49
Polygon -7500403 true true 158 37 172 45 188 59 202 79 217 109 220 130 218 147 204 156 158 156 161 142 170 123 170 102 169 88 165 62
Polygon -7500403 true true 149 66 142 78 139 96 141 111 146 139 148 147 110 147 113 131 118 106 126 71

box
true
0
Polygon -7500403 true true 45 255 255 255 255 45 45 45

butterfly1
true
0
Polygon -16777216 true false 151 76 138 91 138 284 150 296 162 286 162 91
Polygon -7500403 true true 164 106 184 79 205 61 236 48 259 53 279 86 287 119 289 158 278 177 256 182 164 181
Polygon -7500403 true true 136 110 119 82 110 71 85 61 59 48 36 56 17 88 6 115 2 147 15 178 134 178
Polygon -7500403 true true 46 181 28 227 50 255 77 273 112 283 135 274 135 180
Polygon -7500403 true true 165 185 254 184 272 224 255 251 236 267 191 283 164 276
Line -7500403 true 167 47 159 82
Line -7500403 true 136 47 145 81
Circle -7500403 true true 165 45 8
Circle -7500403 true true 134 45 6
Circle -7500403 true true 133 44 7
Circle -7500403 true true 133 43 8

circle
false
0
Circle -7500403 true true 35 35 230

person
false
0
Circle -7500403 true true 155 20 63
Rectangle -7500403 true true 158 79 217 164
Polygon -7500403 true true 158 81 110 129 131 143 158 109 165 110
Polygon -7500403 true true 216 83 267 123 248 143 215 107
Polygon -7500403 true true 167 163 145 234 183 234 183 163
Polygon -7500403 true true 195 163 195 233 227 233 206 159

sheep
false
15
Rectangle -1 true true 90 75 270 225
Circle -1 true true 15 75 150
Rectangle -16777216 true false 81 225 134 286
Rectangle -16777216 true false 180 225 238 285
Circle -16777216 true false 1 88 92

spacecraft
true
0
Polygon -7500403 true true 150 0 180 135 255 255 225 240 150 180 75 240 45 255 120 135

thin-arrow
true
0
Polygon -7500403 true true 150 0 0 150 120 150 120 293 180 293 180 150 300 150

truck-down
false
0
Polygon -7500403 true true 225 30 225 270 120 270 105 210 60 180 45 30 105 60 105 30
Polygon -8630108 true false 195 75 195 120 240 120 240 75
Polygon -8630108 true false 195 225 195 180 240 180 240 225

truck-left
false
0
Polygon -7500403 true true 120 135 225 135 225 210 75 210 75 165 105 165
Polygon -8630108 true false 90 210 105 225 120 210
Polygon -8630108 true false 180 210 195 225 210 210

truck-right
false
0
Polygon -7500403 true true 180 135 75 135 75 210 225 210 225 165 195 165
Polygon -8630108 true false 210 210 195 225 180 210
Polygon -8630108 true false 120 210 105 225 90 210

turtle
true
0
Polygon -7500403 true true 138 75 162 75 165 105 225 105 225 142 195 135 195 187 225 195 225 225 195 217 195 202 105 202 105 217 75 225 75 195 105 187 105 135 75 142 75 105 135 105

wolf
false
0
Rectangle -7500403 true true 15 105 105 165
Rectangle -7500403 true true 45 90 105 105
Polygon -7500403 true true 60 90 83 44 104 90
Polygon -16777216 true false 67 90 82 59 97 89
Rectangle -1 true false 48 93 59 105
Rectangle -16777216 true false 51 96 55 101
Rectangle -16777216 true false 0 121 15 135
Rectangle -16777216 true false 15 136 60 151
Polygon -1 true false 15 136 23 149 31 136
Polygon -1 true false 30 151 37 136 43 151
Rectangle -7500403 true true 105 120 263 195
Rectangle -7500403 true true 108 195 259 201
Rectangle -7500403 true true 114 201 252 210
Rectangle -7500403 true true 120 210 243 214
Rectangle -7500403 true true 115 114 255 120
Rectangle -7500403 true true 128 108 248 114
Rectangle -7500403 true true 150 105 225 108
Rectangle -7500403 true true 132 214 155 270
Rectangle -7500403 true true 110 260 132 270
Rectangle -7500403 true true 210 214 232 270
Rectangle -7500403 true true 189 260 210 270
Line -7500403 true 263 127 281 155
Line -7500403 true 281 155 281 192

wolf-left
false
3
Polygon -6459832 true true 117 97 91 74 66 74 60 85 36 85 38 92 44 97 62 97 81 117 84 134 92 147 109 152 136 144 174 144 174 103 143 103 134 97
Polygon -6459832 true true 87 80 79 55 76 79
Polygon -6459832 true true 81 75 70 58 73 82
Polygon -6459832 true true 99 131 76 152 76 163 96 182 104 182 109 173 102 167 99 173 87 159 104 140
Polygon -6459832 true true 107 138 107 186 98 190 99 196 112 196 115 190
Polygon -6459832 true true 116 140 114 189 105 137
Rectangle -6459832 true true 109 150 114 192
Rectangle -6459832 true true 111 143 116 191
Polygon -6459832 true true 168 106 184 98 205 98 218 115 218 137 186 164 196 176 195 194 178 195 178 183 188 183 169 164 173 144
Polygon -6459832 true true 207 140 200 163 206 175 207 192 193 189 192 177 198 176 185 150
Polygon -6459832 true true 214 134 203 168 192 148
Polygon -6459832 true true 204 151 203 176 193 148
Polygon -6459832 true true 207 103 221 98 236 101 243 115 243 128 256 142 239 143 233 133 225 115 214 114

wolf-right
false
3
Polygon -6459832 true true 170 127 200 93 231 93 237 103 262 103 261 113 253 119 231 119 215 143 213 160 208 173 189 187 169 190 154 190 126 180 106 171 72 171 73 126 122 126 144 123 159 123
Polygon -6459832 true true 201 99 214 69 215 99
Polygon -6459832 true true 207 98 223 71 220 101
Polygon -6459832 true true 184 172 189 234 203 238 203 246 187 247 180 239 171 180
Polygon -6459832 true true 197 174 204 220 218 224 219 234 201 232 195 225 179 179
Polygon -6459832 true true 78 167 95 187 95 208 79 220 92 234 98 235 100 249 81 246 76 241 61 212 65 195 52 170 45 150 44 128 55 121 69 121 81 135
Polygon -6459832 true true 48 143 58 141
Polygon -6459832 true true 46 136 68 137
Polygon -6459832 true true 45 129 35 142 37 159 53 192 47 210 62 238 80 237
Line -16777216 false 74 237 59 213
Line -16777216 false 59 213 59 212
Line -16777216 false 58 211 67 192
Polygon -6459832 true true 38 138 66 149
Polygon -6459832 true true 46 128 33 120 21 118 11 123 3 138 5 160 13 178 9 192 0 199 20 196 25 179 24 161 25 148 45 140
Polygon -6459832 true true 67 122 96 126 63 144
@#$#@#$#@
NetLogo 6.1.1
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
