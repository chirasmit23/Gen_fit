from flask import render_template

def register_workout_routes(app):
    @app.route("/dietplan")
    def dietplan():
        return render_template("UserPages/dietplan.html")
    @app.route("/supplement")
    def supplement_plan():
        return render_template("UserPages/supplements.html")
    @app.route("/exercise")
    def exercise():
        return render_template("UserPages/exercise.html")
    @app.route("/streching")
    def streching():
        return render_template("UserPages/stretching.html")
    @app.route("/My_Plan")
    def My_Plan():
        return render_template("UserPages/My_Plan.html")
    @app.route("/skullcrushers")
    def skullcrushers():
        return render_template("tricepsworkoutdetails/skullcrushers.html")
    @app.route("/dumbbelloverheadextension")
    def dumbbelloverheadextension():
        return render_template("tricepsworkoutdetails/dumbbelloverheadextension.html")
    @app.route("/ezbarcablepushdown")
    def ezbarcablepushdown():
        return render_template("tricepsworkoutdetails/ezbarcablepushdown.html")
    @app.route("/ropepushdown")
    def ropepushdown():
        return render_template("tricepsworkoutdetails/ropepushdown.html")
    @app.route("/seatedoverheaddumbbeltextension")
    def seatedoverheaddumbbeltextension():
        return render_template("tricepsworkoutdetails/seatedoverheaddumbbeltextension.html")
    @app.route("/lyingtricepextension")
    def lyingtricepextension():
        return render_template("tricepsworkoutdetails/lyingtricepextension.html")
    @app.route("/crossbodycableextension")
    def crossbodycableextension():
        return render_template("tricepsworkoutdetails/crossbodycableextension.html")
    @app.route("/dips")
    def dips():
        return render_template("tricepsworkoutdetails/dips.html")
    @app.route("/diamondpushup")
    def diamondpushup():

        return render_template("tricepsworkoutdetails/diamondpushup.html")
    @app.route("/benchdips")
    def benchdips():
        return render_template("tricepsworkoutdetails/benchdips.html")
    @app.route("/close_grip_brench_press")
    def close_grip_brench_press():
        return render_template("tricepsworkoutdetails/closegripbenchpress.html")
    @app.route("/closegrippushup")
    def closegrippushup():
        return render_template("tricepsworkoutdetails/closegrippushup.html")
    @app.route("/ropeburnouts")
    def ropeburnouts():
        return render_template("tricepsworkoutdetails/ropeburnouts.html")
    @app.route("/pushupburnout")
    def pushupburnout():
        return render_template("tricepsworkoutdetails/pushupburnout.html")
    @app.route("/dropsetcablepushdowns")
    def dropsetcablepushdowns():
        return render_template("tricepsworkoutdetails/dropsetcablepushdowns.html")

    @app.route("/halfrepsskullcrusher")
    def halfrepsskullcrusher():
        return render_template("tricepsworkoutdetails/halfrepsskullcrusher.html")
    @app.route("/shoulderworkout")
    def shoulderworkout():
        return render_template("UserPages/shoulderworkout.html")
    @app.route("/legsworkout")
    def legsworkout():
        return render_template("UserPages/legsworkout.html")

    @app.route("/workout/chest")
    def chest_workout():
        return render_template("UserPages/chestworkout.html")

    @app.route("/workout/back")
    def back_workout():
        return render_template("UserPages/backworkout.html")

    @app.route("/workout/biceps")
    def biceps_workout():
        return render_template("UserPages/bicepsworkout.html")

    @app.route("/workout/triceps")
    def triceps_workout():
        return render_template("UserPages/tricepsworkout.html")

    @app.route("/workout/shoulder")
    def shoulder_workout():
        return render_template("UserPages/shoulderworkout.html")

    @app.route("/workout/legs")
    def legs_workout():
        return render_template("UserPages/legsworkout.html")
    @app.route("/overheadbarbellpress")
    def overheadbarbellpress():
        return render_template("shoulderworkoutdetails/overheadbarbellpress.html")

    @app.route("/seateddumbbellpress")
    def seateddumbbellpress():
        return render_template("shoulderworkoutdetails/seateddumbbellpress.html")

    @app.route("/pushpress")
    def pushpress():
        return render_template("shoulderworkoutdetails/pushpress.html")

    @app.route("/machineshoulderpress")
    def machineshoulderpress():
        return render_template("shoulderworkoutdetails/machineshoulderpress.html")
    @app.route("/dumbbelllateralraise")
    def dumbbelllateralraise():
        return render_template("shoulderworkoutdetails/dumbbelllateralraise.html")

    @app.route("/cablelateralraise")
    def cablelateralraise():
        return render_template("shoulderworkoutdetails/cablelateralraise.html")

    @app.route("/leaninglateralraise")
    def leaninglateralraise():
        return render_template("shoulderworkoutdetails/leaninglateralraise.html")

    @app.route("/machinelateralraise")
    def machinelateralraise():
        return render_template("shoulderworkoutdetails/machinelateralraise.html")
    @app.route("/reversepecdeck")
    def reversepecdeck():
        return render_template("shoulderworkoutdetails/reversepecdeck.html")

    @app.route("/reardeltfly")
    def reardeltfly():
        return render_template("shoulderworkoutdetails/reardeltfly.html")

    @app.route("/facepulls")
    def facepulls():
        return render_template("shoulderworkoutdetails/facepulls.html")

    @app.route("/inclinereversefly")
    def inclinereversefly():
        return render_template("shoulderworkoutdetails/inclinereversefly.html")
    @app.route("/burnoutlaterals")
    def burnoutlaterals():
        return render_template("shoulderworkoutdetails/burnoutlaterals.html")

    @app.route("/shoulderpressburnout")
    def shoulderpressburnout():
        return render_template("shoulderworkoutdetails/shoulderpressburnout.html")

    @app.route("/uprightrowburnout")
    def uprightrowburnout():
        return render_template("shoulderworkoutdetails/uprightrowburnout.html")

    @app.route("/halfrepslateralraise")
    def halfrepslateralraise():
        return render_template("shoulderworkoutdetails/halfrepslateralraise.html")
    @app.route("/barbellbacksquat")
    def barbellbacksquat():
        return render_template("legworkoutdetails/barbelbacksquat.html")

    @app.route("/frontsquat")
    def frontsquat():
        return render_template("legworkoutdetails/frontsquat.html")

    @app.route("/romaniandeadlift")
    def romaniandeadlift():
        return render_template("legworkoutdetails/romaniandeadlift.html")

    @app.route("/bulgariansplitsquat")
    def bulgariansplitsquat():
        return render_template("legworkoutdetails/bulgariansplitsquat.html")


    @app.route("/legextension")
    def legextension():
        return render_template("legworkoutdetails/legextension.html")

    @app.route("/hacksquat")
    def hacksquat():
        return render_template("legworkoutdetails/hacksquat.html")

    @app.route("/heelevatedgobletsquat")
    def heelevatedgobletsquat():
        return render_template("legworkoutdetails/heelevatedgobletsquat.html")

    @app.route("/stepups")
    def stepups():
        return render_template("legworkoutdetails/stepups.html")

    @app.route("/seatedlegcurl")
    def seatedlegcurl():
        return render_template("legworkoutdetails/seatedlegcurl.html")

    @app.route("/hipthrust")
    def hipthrust():
        return render_template("legworkoutdetails/hipthrust.html")

    @app.route("/cablepullthrough")
    def cablepullthrough():
        return render_template("legworkoutdetails/cablepullthrough.html")

    @app.route("/glutekickback")
    def glutekickback():
        return render_template("legworkoutdetails/glutekickback.html")


    @app.route("/standingcalfraise")
    def standingcalfraise():
        return render_template("legworkoutdetails/standingcalfraise.html")

    @app.route("/seatedcalfraise")
    def seatedcalfraise():
        return render_template("legworkoutdetails/seatedcalfraise.html")

    @app.route("/jumpsquats")
    def jumpsquats():
        return render_template("legworkoutdetails/jumpsquats.html")

    @app.route("/walkinglunges")
    def walkinglunges():
        return render_template("legworkoutdetails/walkinglunges.html")