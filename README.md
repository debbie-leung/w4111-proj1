README file for Databases Project 1

PostgreSQL account name: dsl2162

URL of web application: http://35.185.67.87:8111/

Implementation details: We basically implemented all the parts in our initial proposal. There were three main categories in our ER diagram. In the user category, we let user to enter their personal information, which is realized by sign up section in our website. The website allows users to update their personal information on profile section. The user can either submit an occurrence or a sequence to the database which is implemented in the submit section of the dashboard. Also, the user can access to her or his access history, which can be shown by the history section of the dashboard. The forth function that a user can do is to vote sequence. The second category of our ER diagram is Sequence category. We implemented a search engine for loggedin and unloggedin users. There are two options for the search engine: a simple engine that takes genus and species and a advance search that gives various options for user to choose. The third category is the occurrence category. The user can submit occurence in the submit section and search for occurrence in advance search. The reference table is shown along with the sequence information.

Two example web pages:
1. User submit: User is able to submit either sequence or occurrence or both for an organism through the submit form on this tab. It inserts data into the database that allows user to submit new sequences or occurrences for the same organism already in the database. The inputs in this page are then used to populate the database, through which other interesting operations, such as advance search, is perform to obtain search results fromt he database.
2. Advance search: The Advance Search feature is implement by using many interesting database operations. The user is asked for select the qualities of the organisms that they want to see the sequence and occurrence. The selections are pass into the function and inserted into the table. The inner join is used to combine the sequence and reference information.
