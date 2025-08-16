-- Sample Books Data for LibriPal
-- Created: 2025-08-16

INSERT INTO books (isbn, title, author, publisher, publication_year, genre, description, total_copies, available_copies, cover_image_url) VALUES

-- Computer Science Books
('9780262033848', 'Introduction to Algorithms', 'Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein', 'MIT Press', 2009, 'Computer Science', 'Comprehensive introduction to algorithms covering design and analysis of algorithms with mathematical rigor.', 3, 3, 'https://images-na.ssl-images-amazon.com/images/I/41T0iBxY8FL._SX440_BO1,204,203,200_.jpg'),

('9780132350884', 'Clean Code: A Handbook of Agile Software Craftsmanship', 'Robert C. Martin', 'Prentice Hall', 2008, 'Computer Science', 'A guide to writing clean, maintainable code with practical examples and best practices.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg'),

('9780135957059', 'The Pragmatic Programmer: Your Journey to Mastery', 'David Thomas, Andrew Hunt', 'Addison-Wesley Professional', 2019, 'Computer Science', 'Updated edition of the classic guide to becoming a better programmer.', 2, 1, 'https://images-na.ssl-images-amazon.com/images/I/41as+WafrFL._SX384_BO1,204,203,200_.jpg'),

('9780134685991', 'Effective Java', 'Joshua Bloch', 'Addison-Wesley Professional', 2017, 'Computer Science', 'Best practices for the Java platform covering new features through Java 9.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/41cQD9aeJZL._SX397_BO1,204,203,200_.jpg'),

('9781617294136', 'Spring in Action', 'Craig Walls', 'Manning Publications', 2018, 'Computer Science', 'Comprehensive guide to the Spring Framework covering Spring Boot and microservices.', 1, 1, 'https://images-na.ssl-images-amazon.com/images/I/51mJr6vEQFL._SX397_BO1,204,203,200_.jpg'),

-- Mathematics Books
('9780471317166', 'Advanced Engineering Mathematics', 'Erwin Kreyszig', 'Wiley', 2011, 'Mathematics', 'Comprehensive coverage of mathematical methods for engineering and science.', 4, 3, 'https://images-na.ssl-images-amazon.com/images/I/51Md7jlNZ9L._SX398_BO1,204,203,200_.jpg'),

('9780321849694', 'Elementary Linear Algebra', 'Howard Anton, Chris Rorres', 'Pearson', 2013, 'Mathematics', 'Introduction to linear algebra with applications and computational techniques.', 3, 2, 'https://images-na.ssl-images-amazon.com/images/I/51KmH2kBNML._SX392_BO1,204,203,200_.jpg'),

('9780321947345', 'Calculus: Early Transcendentals', 'James Stewart', 'Cengage Learning', 2015, 'Mathematics', 'Comprehensive calculus textbook with clear explanations and numerous examples.', 5, 4, 'https://images-na.ssl-images-amazon.com/images/I/51H4kxrWgxL._SX391_BO1,204,203,200_.jpg'),

-- Engineering Books
('9780134670942', 'Engineering Mechanics: Statics & Dynamics', 'Russell C. Hibbeler', 'Pearson', 2015, 'Engineering', 'Fundamental principles of engineering mechanics with practical applications.', 3, 2, 'https://images-na.ssl-images-amazon.com/images/I/51Qx8mO1nAL._SX398_BO1,204,203,200_.jpg'),

('9780134319650', 'Introduction to Electric Circuits', 'Richard C. Dorf, James A. Svoboda', 'Wiley', 2016, 'Engineering', 'Comprehensive introduction to circuit analysis and design.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/51m4rDVGgOL._SX391_BO1,204,203,200_.jpg'),

-- Data Science & AI
('9781449369415', 'Python for Data Analysis', 'Wes McKinney', 'O''Reilly Media', 2017, 'Computer Science', 'Essential tools for data analysis using Python, pandas, and NumPy.', 2, 1, 'https://images-na.ssl-images-amazon.com/images/I/51WILwvk8pL._SX379_BO1,204,203,200_.jpg'),

('9781491946008', 'Introduction to Statistical Learning', 'Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani', 'Springer', 2017, 'Mathematics', 'Accessible introduction to statistical learning methods with R applications.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/41gtTCCfWTL._SX321_BO1,204,203,200_.jpg'),

('9781617295984', 'Deep Learning with Python', 'François Chollet', 'Manning Publications', 2021, 'Computer Science', 'Practical introduction to deep learning using Keras and TensorFlow.', 1, 0, 'https://images-na.ssl-images-amazon.com/images/I/51YiWYzJOgL._SX397_BO1,204,203,200_.jpg'),

-- Web Development
('9781491918661', 'Learning React', 'Alex Banks, Eve Porcello', 'O''Reilly Media', 2020, 'Computer Science', 'Modern approach to learning React including hooks and functional components.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/51Lpj%2B3vlyL._SX379_BO1,204,203,200_.jpg'),

('9781492070511', 'JavaScript: The Definitive Guide', 'David Flanagan', 'O''Reilly Media', 2020, 'Computer Science', 'Comprehensive reference and tutorial for JavaScript programming.', 2, 1, 'https://images-na.ssl-images-amazon.com/images/I/51UlRWuZqSL._SX379_BO1,204,203,200_.jpg'),

('9780134092669', 'Web Development with Node and Express', 'Ethan Brown', 'O''Reilly Media', 2019, 'Computer Science', 'Building web applications with Node.js and the Express framework.', 1, 1, 'https://images-na.ssl-images-amazon.com/images/I/51J-VqGR2EL._SX379_BO1,204,203,200_.jpg'),

-- Physics Books
('9781118230725', 'University Physics with Modern Physics', 'Hugh D. Young, Roger A. Freedman', 'Pearson', 2015, 'Physics', 'Comprehensive university-level physics covering classical and modern physics.', 4, 3, 'https://images-na.ssl-images-amazon.com/images/I/51QyN1vbJPL._SX394_BO1,204,203,200_.jpg'),

('9781107189638', 'Introduction to Quantum Mechanics', 'David J. Griffiths, Darrell F. Schroeter', 'Cambridge University Press', 2018, 'Physics', 'Clear introduction to quantum mechanics with worked examples.', 2, 1, 'https://images-na.ssl-images-amazon.com/images/I/51Dwy4QKJrL._SX347_BO1,204,203,200_.jpg'),

-- Design & Art
('9780321934956', 'Don''t Make Me Think', 'Steve Krug', 'New Riders', 2013, 'Design', 'Common-sense approach to web usability and user experience design.', 1, 1, 'https://images-na.ssl-images-amazon.com/images/I/51pnouuPO5L._SX387_BO1,204,203,200_.jpg'),

('9780321965516', 'The Design of Everyday Things', 'Don Norman', 'Basic Books', 2013, 'Design', 'Classic book on user-centered design and the psychology of design.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/41hZC0zcq3L._SX323_BO1,204,203,200_.jpg'),

-- Business & Economics
('9780062316097', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'Harper', 2014, 'History', 'Thought-provoking look at human history and civilization.', 3, 2, 'https://images-na.ssl-images-amazon.com/images/I/41Hbv6xEh6L._SX323_BO1,204,203,200_.jpg'),

('9780062457714', 'The Lean Startup', 'Eric Ries', 'Crown Business', 2011, 'Business', 'How to build successful startups using lean methodology.', 2, 1, 'https://images-na.ssl-images-amazon.com/images/I/41SVEoXP2EL._SX324_BO1,204,203,200_.jpg'),

-- Database & Systems
('9780321884497', 'Database System Concepts', 'Abraham Silberschatz, Henry F. Korth, S. Sudarshan', 'McGraw-Hill Education', 2019, 'Computer Science', 'Comprehensive introduction to database management systems.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/51tRaSGXPuL._SX394_BO1,204,203,200_.jpg'),

('9780134670959', 'Operating System Concepts', 'Abraham Silberschatz, Peter Baer Galvin, Greg Gagne', 'Wiley', 2018, 'Computer Science', 'Essential concepts in operating systems design and implementation.', 2, 1, 'https://images-na.ssl-images-amazon.com/images/I/51rVfgCyq8L._SX394_BO1,204,203,200_.jpg'),

-- Additional Popular Books
('9780135166307', 'Computer Networks', 'Andrew S. Tanenbaum, David J. Wetherall', 'Pearson', 2021, 'Computer Science', 'Comprehensive coverage of computer networking concepts and protocols.', 2, 2, 'https://images-na.ssl-images-amazon.com/images/I/51f1rV6cUQL._SX394_BO1,204,203,200_.jpg');

-- Update available copies to create some reservations scenarios
UPDATE books SET available_copies = 0 WHERE title IN ('Deep Learning with Python', 'The Pragmatic Programmer: Your Journey to Mastery');