from .models import *
from .serializers import *
from django.db.models import Q , F

def fetch_get_course(id):
    return Course.objects.get(id=id)

def fetch_filter_course(id):
    course = Course.objects.get(university=id)
    return course

def fetch_filter_course_serialized(id):
    course = Course.objects.filter(university=id)
    course_serializer = CourseSerializer(course,many=True)
    return course_serializer.data

def fetch_get_stream(id):
    return Stream.objects.get(course=id)

def fetch_filter_stream_serialized(id):
    stream = Stream.objects.filter(course=id)
    stream_serializer = StreamSerializer(stream,many=True)
    return stream_serializer.data
    

def create_new_semester_fees(request,stream,substream,semester,all_fees_data):##modified by Avani 14/08
    for i in range(0,int(semester)):
        print(all_fees_data[i])
        if substream != '' and substream != None:
            try:
                semesterfees = SemesterFees.objects.get(Q(stream = Stream.objects.get(id=stream)) & Q(substream = SubStream.objects.get(id=substream)) & Q(sem=all_fees_data[i]['semester']))##modified by Avani 14/08
                update_semester_fees = SemesterFees(
                    id=semesterfees.id,
                    stream= Stream.objects.get(id=stream),
                    substream=SubStream.objects.get(id=substream),##added by Avani 14/08
                    tutionfees=all_fees_data[i][f"tution{i+1}"],
                    examinationfees=all_fees_data[i][f"exam{i+1}"],
                    bookfees=all_fees_data[i][f"book{i+1}"],
                    resittingfees=all_fees_data[i][f"resitting{i+1}"],
                    entrancefees=all_fees_data[i][f"entrance{i+1}"],
                    extrafees=all_fees_data[i][f"extra{i+1}"],
                    discount=all_fees_data[i][f"discount{i+1}"],
                    totalfees=all_fees_data[i][f"total{i+1}"],
                    sem=all_fees_data[i]['semester'],
                    created_by=request.user.id,
                )
                update_semester_fees.save()
            except SemesterFees.DoesNotExist:
                
                create_semester_fees = SemesterFees(
                    stream= Stream.objects.get(id=stream),
                    substream = SubStream.objects.get(id=substream),
                    tutionfees=all_fees_data[i][f"tution{i+1}"],
                    examinationfees=all_fees_data[i][f"exam{i+1}"],
                    bookfees=all_fees_data[i][f"book{i+1}"],
                    resittingfees=all_fees_data[i][f"resitting{i+1}"],
                    entrancefees=all_fees_data[i][f"entrance{i+1}"],
                    extrafees=all_fees_data[i][f"extra{i+1}"],
                    discount=all_fees_data[i][f"discount{i+1}"],
                    totalfees=all_fees_data[i][f"total{i+1}"],
                    sem=all_fees_data[i]['semester'],
                    created_by=request.user.id,
                )
                create_semester_fees.save()
        else:
            try:
                semesterfees = SemesterFees.objects.get(Q(stream = Stream.objects.get(id=stream)) & Q(substream__isnull=True) & Q(sem=all_fees_data[i]['semester']))##modified by Avani 14/08
                update_semester_fees = SemesterFees(
                    id=semesterfees.id,
                    stream= Stream.objects.get(id=stream),
                    substream=None,##added by Avani 14/08
                    tutionfees=all_fees_data[i][f"tution{i+1}"],
                    examinationfees=all_fees_data[i][f"exam{i+1}"],
                    bookfees=all_fees_data[i][f"book{i+1}"],
                    resittingfees=all_fees_data[i][f"resitting{i+1}"],
                    entrancefees=all_fees_data[i][f"entrance{i+1}"],
                    extrafees=all_fees_data[i][f"extra{i+1}"],
                    discount=all_fees_data[i][f"discount{i+1}"],
                    totalfees=all_fees_data[i][f"total{i+1}"],
                    sem=all_fees_data[i]['semester'],
                    created_by=request.user.id,
                )
                update_semester_fees.save()
            except SemesterFees.DoesNotExist:
                create_semester_fees = SemesterFees(
                    stream= Stream.objects.get(id=stream),
                    substream = None,
                    tutionfees=all_fees_data[i][f"tution{i+1}"],
                    examinationfees=all_fees_data[i][f"exam{i+1}"],
                    bookfees=all_fees_data[i][f"book{i+1}"],
                    resittingfees=all_fees_data[i][f"resitting{i+1}"],
                    entrancefees=all_fees_data[i][f"entrance{i+1}"],
                    extrafees=all_fees_data[i][f"extra{i+1}"],
                    discount=all_fees_data[i][f"discount{i+1}"],
                    totalfees=all_fees_data[i][f"total{i+1}"],
                    sem=all_fees_data[i]['semester'],
                    created_by=request.user.id,
                )
                create_semester_fees.save()
            
    return "yes"

def create_new_year_fees(request,stream, substream, year,all_fees_data):##mofified by Avani 14/08
    for i in range(0,int(year)):
        if substream != '' and substream != None:
            try:
                yearfees = YearFees.objects.get(Q(stream = Stream.objects.get(id=stream)) & Q(substream= SubStream.objects.get(id=substream)) & Q(year=all_fees_data[i]['year']))##modified by Avani 14/08
                update_year_fees = YearFees(
                        id=yearfees.id,
                        stream= Stream.objects.get(id=stream),
                        substream = SubStream.objects.get(id=substream),##added by Avani 14/08
                        tutionfees=all_fees_data[i][f"tution{i+1}"],
                        examinationfees=all_fees_data[i][f"exam{i+1}"],
                        bookfees=all_fees_data[i][f"book{i+1}"],
                        resittingfees=all_fees_data[i][f"resitting{i+1}"],
                        entrancefees=all_fees_data[i][f"entrance{i+1}"],
                        extrafees=all_fees_data[i][f"extra{i+1}"],
                        discount=all_fees_data[i][f"discount{i+1}"],
                        totalfees=all_fees_data[i][f"total{i+1}"],
                        year=all_fees_data[i]['year'],
                        created_by=request.user.id,
                    )
                update_year_fees.save()
            except YearFees.DoesNotExist:
                create_year_fees = YearFees(
                    stream= Stream.objects.get(id=stream),
                    substream = SubStream.objects.get(id=substream),##added by Avani 14/08
                    tutionfees=all_fees_data[i][f"tution{i+1}"],
                    examinationfees=all_fees_data[i][f"exam{i+1}"],
                    bookfees=all_fees_data[i][f"book{i+1}"],
                    resittingfees=all_fees_data[i][f"resitting{i+1}"],
                    entrancefees=all_fees_data[i][f"entrance{i+1}"],
                    extrafees=all_fees_data[i][f"extra{i+1}"],
                    discount=all_fees_data[i][f"discount{i+1}"],
                    totalfees=all_fees_data[i][f"total{i+1}"],
                    year=all_fees_data[i]['year'],
                    created_by=request.user.id,
                    )
                create_year_fees.save()
                     
               
        else:
            try:
                yearfees = YearFees.objects.get(Q(stream = Stream.objects.get(id=stream)) & Q(substream__isnull=True) & Q(year=all_fees_data[i]['year']))##modified by Avani 14/08
                update_year_fees = YearFees(
                        id=yearfees.id,
                        stream= Stream.objects.get(id=stream),
                        substream = None,##added by Avani 14/08
                        tutionfees=all_fees_data[i][f"tution{i+1}"],
                        examinationfees=all_fees_data[i][f"exam{i+1}"],
                        bookfees=all_fees_data[i][f"book{i+1}"],
                        resittingfees=all_fees_data[i][f"resitting{i+1}"],
                        entrancefees=all_fees_data[i][f"entrance{i+1}"],
                        extrafees=all_fees_data[i][f"extra{i+1}"],
                        discount=all_fees_data[i][f"discount{i+1}"],
                        totalfees=all_fees_data[i][f"total{i+1}"],
                        year=all_fees_data[i]['year'],
                        created_by=request.user.id,
                    )
                update_year_fees.save()
            
            except YearFees.DoesNotExist:
            
                create_year_fees = YearFees(
                    stream= Stream.objects.get(id=stream),
                    substream = None,##added by Avani 14/08
                    tutionfees=all_fees_data[i][f"tution{i+1}"],
                    examinationfees=all_fees_data[i][f"exam{i+1}"],
                    bookfees=all_fees_data[i][f"book{i+1}"],
                    resittingfees=all_fees_data[i][f"resitting{i+1}"],
                    entrancefees=all_fees_data[i][f"entrance{i+1}"],
                    extrafees=all_fees_data[i][f"extra{i+1}"],
                    discount=all_fees_data[i][f"discount{i+1}"],
                    totalfees=all_fees_data[i][f"total{i+1}"],
                    year=all_fees_data[i]['year'],
                    created_by=request.user.id,
                )
                create_year_fees.save()
            
    return "yes"

















