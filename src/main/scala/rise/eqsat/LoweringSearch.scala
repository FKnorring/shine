package rise.eqsat

object LoweringSearch {
  def init(): LoweringSearch = new LoweringSearch(
    filter = StandardConstraintsPredicate
  )
}

// TODO: enable giving a sketch, maybe merge with GuidedSearch?
class LoweringSearch(var filter: Predicate) {
  private def topLevelAnnotation(t: Type): BeamExtractRW.TypeAnnotation = {
    import RWAnnotationDSL._
    t.node match {
      case NatFunType(t) => nFunT(topLevelAnnotation(t))
      case DataFunType(t) => dtFunT(topLevelAnnotation(t))
      case AddrFunType(t) => aFunT(topLevelAnnotation(t))
      case FunType(ta, tb) =>
        if (!ta.node.isInstanceOf[DataTypeNode[_, _]]) {
          throw new Exception("top level higher-order functions are not supported")
        }
        read ->: topLevelAnnotation(tb)
      case _: DataTypeNode[_, _] =>
        write
      case _ =>
        throw new Exception(s"did not expect type $t")
    }
  }

  def run(normalForm: NF,
          costFunction: CostFunction[_],
          startBeam: Seq[Expr],
          loweringRules: Seq[Rewrite],
          annotations: Option[(BeamExtractRW.TypeAnnotation, Map[Int, BeamExtractRW.TypeAnnotation])] = None): Option[Expr] = {
    println("---- lowering")
    val egraph = EGraph.empty()
    val normBeam = startBeam.map(normalForm.normalize)
    println(s"normalized: $normBeam")

    val expectedAnnotations = annotations match {
      case Some(annotations) => annotations
      case None => (topLevelAnnotation(normBeam.head.t), Map.empty[Int, BeamExtractRW.TypeAnnotation])
    }

    val rootId = normBeam.map(egraph.addExpr)
      .reduce[EClassId] { case (a, b) => egraph.union(a, b)._1 }
    egraph.rebuild(Seq(rootId))

    val r = Runner.init()
      .withTimeLimit(java.time.Duration.ofMinutes(1))
      .withMemoryLimit(4L * 1024L * 1024L * 1024L /* 4GiB */)
      .withNodeLimit(1_000_000)
      .run(egraph, filter, loweringRules, Seq()/*normalForm.directedRules*/, Seq(rootId))
    r.printReport()

    util.printTime("lowered extraction time", {
      val tmp = Analysis.oneShot(BeamExtractRW(1, costFunction), egraph)(egraph.find(rootId))
      
      println(s"Expected annotations: $expectedAnnotations")
      println("Available annotations:")
      tmp.keys.foreach(println)
      
      // Get the type from the root EClass
      val rootType = egraph.classes(rootId).t
      
      // Find any annotation that is compatible with the expected annotations
      val result = tmp.find { case (inferredAnnotations, beam) =>
        // Check if the inferred annotation is compatible with the expected annotation
        val (inferredAccess, inferredEnv) = inferredAnnotations
        val (expectedAccess, expectedEnv) = expectedAnnotations
        
        // First check the environments are compatible
        val envCompatible = BeamExtractRW.mergeEnv(inferredEnv, expectedEnv).isDefined
        if (!envCompatible) {
          println(s"Environment mismatch: inferred=$inferredEnv expected=$expectedEnv")
        }
        
        // Helper function for recursive subtyping checks
        def subtypeRec(inferred: BeamExtractRW.TypeAnnotation, expected: BeamExtractRW.TypeAnnotation, t: TypeId): Boolean = {
          (inferred, expected) match {
            case (BeamExtractRW.DataTypeAnnotation(x), BeamExtractRW.DataTypeAnnotation(y)) =>
              // Allow read to be compatible with write for non-array types
              (x == y) || (x == rise.core.types.read && BeamExtractRW.notContainingArrayType(t.asInstanceOf[DataTypeId], egraph))
            
            case (BeamExtractRW.NotDataTypeAnnotation(x), BeamExtractRW.NotDataTypeAnnotation(y)) =>
              import rise.eqsat.TypeNode._
              (x, y) match {
                case (FunType(aIn, aOut), FunType(bIn, bOut)) =>
                  egraph(t) match {
                    case FunType(inT, outT) =>
                      // Contravariant in input (swap inferred/expected), covariant in output
                      subtypeRec(bIn, aIn, inT) && subtypeRec(aOut, bOut, outT)
                    case _ => false
                  }
                case (NatFunType(aOut), NatFunType(bOut)) =>
                  egraph(t) match {
                    case NatFunType(outT) => subtypeRec(aOut, bOut, outT)
                    case _ => false
                  }
                case (DataFunType(aOut), DataFunType(bOut)) =>
                  egraph(t) match {
                    case DataFunType(outT) => subtypeRec(aOut, bOut, outT)
                    case _ => false
                  }
                case (AddrFunType(aOut), AddrFunType(bOut)) =>
                  egraph(t) match {
                    case AddrFunType(outT) => subtypeRec(aOut, bOut, outT)
                    case _ => false
                  }
                case _ => x == y
              }
            case _ => false
          }
        }
        
        // Then check the access annotations are compatible via subtyping
        val accessCompatible = subtypeRec(inferredAccess, expectedAccess, rootType)
        if (!accessCompatible) {
          println(s"Access annotation mismatch: inferred=$inferredAccess expected=$expectedAccess")
          println(s"Type context: rootType=$rootType")
        }
        
        envCompatible && accessCompatible
      }
      
      if (result.isEmpty) {
        println("No compatible annotations found!")
      }
      
      result.flatMap(_._2.headOption.map(x => ExprWithHashCons.expr(egraph)(x._2)))
    })
  }
}
