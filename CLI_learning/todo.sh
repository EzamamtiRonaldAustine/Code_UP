#!/bin/bash
# Simple To-Do list Manager

TODO_FILE="todo.txt"

# Making sure the tod  file exists
if [! -f "$TODO_FILE"]; then
	touch "$TODO_FILE"
fi

while true; do
	echo ""
	echo " To-Do List Manager"
	echo "-------------------"
	echo "1. View tasks"
	echo "2. Add a task"
	echo "3. Remove a task"
	echo "4. Quit"
	echo -n "Choose an option [1-4]:"
	read choice

	case $choice in
		1)
			echo ""
			echo "Current Tasks:"
			if [-s "$TODO_FILE"]; then
				nl -w2 -s". " "$TODO_FILE"
			else
				echo "No tasks yet "
			fi
			;;
		2)
                        echo -n "Enter new task:"
			read task
                        if [-n "$task"]; then
                                echo "$task" >> "$TODO_FILE"
				echo "Task added"
                        else
                                echo "Task cannot be empty "
                        fi
                        ;;
		3)
                        echo ""
			nl -w2 -s". " "$TODO_FILE"
                        echo -n "Enter task number to remove:"
			read num
                        if [-n "$num"]; then
				sed -i "${num}d" "$TODO_FILE"
                                echo "Task removed"
                        else
                                echo "Invalid number "
                        fi
                        ;;
		4)
                        echo "Goodbye"
                        break
                        ;;
		*)
                        echo "Invalid choice"
                        ;;
	esac
done
