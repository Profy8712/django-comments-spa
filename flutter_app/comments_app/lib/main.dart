import 'package:flutter/material.dart';
import 'features/comments/ui/comments_page.dart';

void main() {
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Comments App',
      theme: ThemeData(useMaterial3: true),
      home: const CommentsPage(),
    );
  }
}
