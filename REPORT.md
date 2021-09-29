## Author

    Seth Melhoff  
    UTEP Fall 2021  
    CS 4175: Parallel Computing  
<br>
<br>

## Info

This repository is for assignment 2: Map-Reduce.  
The program [mapReduce](mapReduce.py) searches for a set of words within the works of Shakespeare.  
There are two different ways the searching is implemented both in serial and parallel.  
1. Iterate through the list of words, checking a master list containing all words in the document.  
2. Iterate through each document, checking the list for each word.  
<br>
<br>

## How to use

Tested and verified working on Python 3.6.10  
Run 'mapReduce.py' with the arguments '-w' , '-d' , or '-p'. Argument p is optional. 

    -e prints out the expected frequency results.  
    -w specifies counting the frequency by iterating through words.  
    -d specifies counting the frequency by iterating through documents.  
    -p specifies running in parallel.  
        Using with '-w' distributes the words among available processes.  
        Using with '-d' distributes the documents among available processes.
    use OMP_NUM_THREADS=# to specify how many threads to use in parallel.
<br>
<br>

## Example

```python
word serial:
    python3 mapReduce.py -w

document serial:
    python3 mapReduce.py -d

word parallel:
    python3 mapReduce.py -w -p

document parallel:
    python3 mapReduce.py -d -p

word parallel with 4 threads:
    OMP_NUM_THREADS=4 python3 mapReduce.py -w -p
```
<br>
<br>

## Performance

The following are results generated using the different methods, the average time of 3 runs.  

**word serial**:  
```python
python3 mapReduce.py -w  
    Total search time: 5.9887 seconds
    Total run time: 5.9889 seconds
```

**document serial**:  
```python
python3 mapReduce.py -d  
    Total search time: 6.0722 seconds
    Total run time: 6.0723 seconds 
```

**word parallel**:  
```python
python3 mapReduce.py -w -p (OMP_NUM_THREADS=1)
    Total search time: 5.9026 seconds
    Total run time: 5.9030 seconds

python3 mapReduce.py -w -p (OMP_NUM_THREADS=2)
    Total search time: 3.5738 seconds
    Total run time: 3.5741 seconds

python3 mapReduce.py -w -p (OMP_NUM_THREADS=4)
    Total search time: 1.5341 seconds
    Total run time: 1.5346 seconds

python3 mapReduce.py -w -p (OMP_NUM_THREADS=8)
    Total search time: 1.2561 seconds
    Total run time: 1.2568 seconds
```

**document parallel**:  
```python
python3 mapReduce.py -d -p (OMP_NUM_THREADS=1)
    Total search time: 5.0441 seconds
    Total run time: 5.0445 seconds

python3 mapReduce.py -d -p (OMP_NUM_THREADS=2)
    Total search time: 4.6054 seconds
    Total run time: 4.6058 seconds

python3 mapReduce.py -d -p (OMP_NUM_THREADS=4)
    Total search time: 1.7693 seconds
    Total run time: 1.7696 seconds

python3 mapReduce.py -d -p (OMP_NUM_THREADS=8)
    Total search time: 0.9678 seconds
    Total run time: 0.9681 seconds
```
<br>
<br>

## Issues

The biggest issue I ran into happened when I was trying to implement the parallel part based on the documents.  
I used the provided example for iterating though a list of documents, but I didn't pay attention to the lock.  
This caused the resulting word counts to be completely different than I expected them to be.  
I realized that each process was accessing the dictionary without waiting for the others to update it.  
After going back and looking at the examples again, I eventually noticed use of lock, acquire, and release.  

Another issue that I ran into had to do with the provided word counts.  
Before remembering the word counts were provided, I decided to count each word with the help of notepad++.  
I searched for each one, within all opened documents, and realized words containing the search word would be counted.  
For example, if you search for the word 'you', the word 'young' would be counted.  
I realized that we shouldn't be counting those words, so I adjusted my code to not include them.  
This causes the provided word count to not match the output word count.

These are the counts I ended up with after ignoring words containing the search word.
```python
realWordFreq = {'blood': 719,
                'death': 963, 
                'hamlet': 474, 
                'hate': 188,
                'heart': 1124, 
                'henry': 612, 
                'honest': 309, 
                'king': 3033,
                'love': 2399, 
                'macbeth': 288, 
                'my': 13184, 
                'night': 825,
                'poison': 98, 
                'sleep': 272, 
                'time': 1180,
                'you': 14580}
```
<br>
<br>

## Conclusion

After running all the tests, I realized that increasing the number of threads speeds up the process time to a certain point.  
When you have 8 documents, and are distributing each one among processes, after 8 threads, there is no significant performance increase.  
I believe this happens because with 8 threads, you have already distributed the amount of work in the best way possible.  
It seemed like no matter how many more threads were added, the performance increase started to hit a limit.  
In the case of the word parallel method, the total run time kept getting closer to 1 second.  

Another thing I noticed is that the performance of the serial methods almost matched the parallel methods with 1 thread.  
This made me realize that serial algorithms are basically like only having 1 thread available to perform the work.  
I can see why having multiple threads, or even just one extra for the matter, would increase performance greatly.

This assignment took me a full day to complete.  
A big portion of it was spent reviewing all of the provided examples.  
Without them, I would not properly know how to use a lock.  
<br>
<br>

## CPUINFO

    model name	: AMD Ryzen 9 5900X 12-Core Processor            
        24     216    1464