from manager.models.Stack import Stack

stack = Stack.objects.filter(status=1).distinct()
for st in stack:
    print(st.email)
