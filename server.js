const express = require('express');
const bodyParser = require('body-parser');
const Groq = require('groq-sdk');
// require('dotenv').config(); // Uncomment if using a .env for the API key

// Initialize Groq with API key
const groq = new Groq({ apiKey: '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' });

const app = express();

// Middleware for parsing form data
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files (like CSS if needed)
app.use(express.static('public'));

// Route for displaying the form
app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>Workout Planner</title>
      </head>
      <body>
        <h1>Enter Your Fitness Goal</h1>
        <form action="/workout" method="post">
          <label for="fitnessGoal">Fitness Goal:</label>
          <select id="fitnessGoal" name="fitnessGoal" required>
            <option value="weight loss">Weight Loss</option>
            <option value="muscle gain">Muscle Gain</option>
            <option value="maintain weight">Maintain Weight</option>
          </select><br><br>

          <input type="submit" value="Get Workout Plan">
        </form>
      </body>
    </html>
  `);
});

// Handle form submission
app.post('/workout', async (req, res) => {
  const { fitnessGoal } = req.body;

  // Function to get workout plan from Groq API
  async function getWorkoutPlan(fitnessGoal) {
    const prompt = `
      Create a daily-ordered 7-day workout plan for the fitness goal of '${fitnessGoal}'.
      Each day should be labeled 'Day 1' to 'Day 7' and include essential exercises, with two rest days.
      Avoid extra descriptions or explanations.
    `;

    // Send request to Groq API
    const chatCompletion = await groq.chat.completions.create({
      "messages": [
        {
          "role": "user",
          "content": prompt
        }
      ],
      "model": "llama3-8b-8192",
      "temperature": 0.7,
      "max_tokens": 1024,
      "top_p": 1,
      "stream": false,
      "stop": null
    });

    return chatCompletion.choices[0].message.content;
  }

  try {
    // Get workout plan from the Groq API
    const workoutPlanList = await getWorkoutPlan(fitnessGoal);

    // Clean up the response and convert it to a formatted HTML list
    const workoutPlan = workoutPlanList
      .split('\n')
      .filter(line => line.trim().length > 0)
      .map(day => `<li>${day.trim()}</li>`)
      .join('');

    // Send the response back to the user
    res.send(`
      <html>
        <head><title>Workout Plan</title></head>
        <body>
          <h1>Your Weekly Workout Plan for ${fitnessGoal.charAt(0).toUpperCase() + fitnessGoal.slice(1)}</h1>
          <ul>
            ${workoutPlan}
          </ul>
          <a href="/">Back</a>
        </body>
      </html>
    `);
  } catch (error) {
    console.error('Error:', error);
    res.send('There was an error processing your request.');
  }
});

// Start the server
const port = 4000;
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
